import os.path
import pickle
import subprocess
import sys
import threading
import time
from multiprocessing import shared_memory
from typing import List,Iterable

import numpy as np

from .fault_detection import DetectOutput
from .meta import FaultInfo
from .mixin_camera import CameraMixin
from .mixin_lightning import LightningMixin
from .mixin_prepare import PrepareMixin
from .mixin_save import SaveMixin
from .mixin_setting import SettingMixin
from .mixin_vsampler import VSamplerMixin
from ..config import config

WRITE_FINISHED_FLAG = 0
DETECT_FINISHED_FLAG = 1

# worker 单次检测的最长等待时间, 超时按 worker 异常处理
WORKER_TIMEOUT = 30
# 放电缺陷的去抖窗口: 窗口内的连续事件合并, 窗口结束后立即允许下一次上报
LIGHTNING_DEBOUNCE = 0.3


class WorkerOutput():
    def get(self) -> List[DetectOutput]:
        raise NotImplementedError()


class WorkerCrashError(RuntimeError):
    """ worker 子进程异常退出 / 超时 / 输出损坏 """


work_cache = {}


def _cleanup_work(entry):
    """ 清理 work 缓存项: 杀掉子进程并释放共享内存 """
    task, img_shm, op_shm, out_shm, _, _ = entry
    try:
        if task.poll() is None:
            task.kill()
    except Exception as e:
        print(f'[System][Pipeline] 关闭 worker 进程失败: {e}')
    for shm in (img_shm, op_shm, out_shm):
        try:
            shm.close()
            shm.unlink()
        except Exception:
            pass


def init_work(width, height, imgsize, ctx: str):
    """ 初始化一个 work"""
    if ctx in work_cache:
        task, img_shm, op_shm, out_shm, _width, _height = work_cache[ctx]
        if task.poll() is None and _width == width and _height == height and img_shm.size == imgsize:
            return img_shm, op_shm, out_shm, task
        else:
            if task.poll() is not None:
                print(f'[System][Pipeline] Worker 进程已退出(code={task.returncode}), 重新启动...')
            else:
                print('[System][Pipeline] 原 Worker 参数不匹配, 重新启动...')
            # 旧资源必须先释放, 否则 Windows 下句柄泄漏
            _cleanup_work(work_cache.pop(ctx))

    # 共享内存
    print('[System][Pipeline] 分配共享内存.')
    img_shm = shared_memory.SharedMemory(create=True, size=imgsize)  # 只要 1 个字节
    op_shm = shared_memory.SharedMemory(create=True, size=2)
    out_shm = shared_memory.SharedMemory(create=True, size=2 ** 16)

    print('[System][Pipeline] 解析器路径:', sys.executable)

    if getattr(sys, 'frozen', False):
        # 用户环境
        print('[System][Pipeline] 用户环境...')
        exe_path = os.path.join(os.getcwd(), "detect_worker", "detect_worker.exe")
        print('[System][Pipeline] exe路径:', exe_path)
        exe_path = [exe_path]
    else:
        # 开发环境
        print('[System][Pipeline] 开发环境...')
        print('[System][Pipeline] 解析器路径:', sys.executable)
        assert str(sys.executable).endswith('python.exe'), ''
        start_path = os.path.join(os.getcwd(), 'core', 'pipeline', 'detect_worker.py')
        exe_path = [sys.executable, start_path, ]

    task = subprocess.Popen(exe_path + ['--width', str(width),
                                        '--height', str(height),
                                        '--img_shm_name', img_shm.name,
                                        '--op_shm_name', op_shm.name,
                                        '--out_shm_name', out_shm.name,
                                        ],
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    work_cache[ctx] = (task, img_shm, op_shm, out_shm, width, height)
    return img_shm, op_shm, out_shm, task


def detect_by_work(img: np.ndarray, ctx) -> WorkerOutput:
    """ 使用 worker 进程 异步处理, 加快速度"""
    img_shm, op_shm, out_shm, task = init_work(width=img.shape[1], height=img.shape[0], imgsize=img.nbytes, ctx=ctx)

    # 将 img 拷贝到共享内存
    b = np.ndarray(img.shape, dtype=img.dtype, buffer=img_shm.buf)
    b[:] = img[:]
    # reset : wait detect finish
    op_shm.buf[DETECT_FINISHED_FLAG] = 0
    op_shm.buf[WRITE_FINISHED_FLAG] = 1

    def wapper():
        start = time.time()
        while op_shm.buf[DETECT_FINISHED_FLAG] != 1:
            # worker 进程死亡检查: 否则主线程会永久挂起
            if task.poll() is not None:
                raise WorkerCrashError(f'worker 进程异常退出, 返回码: {task.returncode}')
            if time.time() - start > WORKER_TIMEOUT:
                raise WorkerCrashError(f'worker 检测超时({WORKER_TIMEOUT}s)')
            time.sleep(0.01)
        # 先获取数据大小, 然后读取数据
        data_length = int.from_bytes(out_shm.buf[-1024:], byteorder='big')
        if data_length > len(out_shm.buf) - 1024:
            raise WorkerCrashError(f'worker 输出数据越界: {data_length}')
        output: List[DetectOutput] = pickle.loads(out_shm.buf[:data_length])

        # reset
        op_shm.buf[DETECT_FINISHED_FLAG] = 0
        op_shm.buf[WRITE_FINISHED_FLAG] = 0

        return [DetectOutput(**o) for o in output]

    output = WorkerOutput()
    output.get = wapper
    return output


class FaultDetectionPipeline(SettingMixin, PrepareMixin, SaveMixin, VSamplerMixin, CameraMixin, LightningMixin):

    def __init__(self):
        VSamplerMixin.__init__(self)
        CameraMixin.__init__(self)
        LightningMixin.__init__(self)

        # 当前批次开启时的累计距离
        self._accumulatedDistance_for_batch = 0
        # 处理的fps
        self._process_time = None
        # 最后处理的缺陷
        self._last_faults = None
        # 报警输出通道 (IO 卡物理通道 0~7)
        self._warning_ch = int(config.get(config.IOCard_WarningChannel))
        # 报警重置的定时器 3s
        # 0 触发
        self._warning_reset_lambda = lambda: self._io_card.setOutPutData(**{f'ch{self._warning_ch}': 1})
        self._warning_reset = None
        self.last_warning_time = None
        # 报警持续时间(秒), 与文档保持一致
        self.warning_duration = 3
        # 连续缺陷时节流重新触发报警的间隔(秒): 等于报警持续时间,
        # 使连续缺陷期间报警可以持续
        self.warning_interval = 3
        # 放电去抖状态
        self._lightning_pending = False
        self._lightning_next_time = 0.0

    def start(self):
        """ start detection pipeline """
        self._location_timer.start()
        for thread_func in (self._image_detect_thread, self._lightning_detect_thread):
            t = threading.Thread(target=thread_func)
            t.daemon = True
            t.start()

    def swapBatch(self, batch_name: str,woker_name:str):
        super(FaultDetectionPipeline, self).setBatchName(batch_name)
        super(FaultDetectionPipeline, self).setWorkerName(woker_name)
        self._accumulatedDistance_for_batch = self.accumulatedDistance()

    def setModelConfig(self, modelConfig: 'ModelConfig' or str):
        super(FaultDetectionPipeline, self).setModelConfig(modelConfig=modelConfig)
        config = self.modelConfig()
        # 更新光源控制器的曝光组
        self.setLightGroup(*(config.exposureBatch[ctx] for ctx in self.CAMERA_LIST))

    def _image_detect_thread(self):
        """ 检测线程: 对于四个通道的摄像头数据进行图像处理"""
        def detect_image():
            # ===========================
            # 读取图片, 图像识别
            # ==========================
            imgs = {k: None if info.camera is None else info.camera.read() for k, info in self.channel_bus.items()}

            # 预处理图像
            # 同时判断改管线是否需要处理
            if self.modelConfig() is not None:
                # 如果不使能, 则置空后续会掉过处理
                imgs = {k: v if self.modelConfig().enable[k] else None for k, v in imgs.items()}
                self.prepare(images=imgs, modelConfig=self.modelConfig())
            # =========================================
            # 处理图片
            # 多进程, 需要异步获取结果
            # =========================================
            worker, is_exist_fault = {}, False
            for k, img in imgs.items():
                if img is None:
                    self.channel_bus[k].clear()
                else:
                    is_exist_fault = True
                    self.channel_bus[k].detect_image = img
                    self.channel_bus[k].oringe_image = img
                    try:
                        worker[k] = detect_by_work(img, ctx=k)
                    except Exception as e:
                        print(f'[System][Pipeline] 通道 {k} worker 提交失败: {e}, 跳过本帧')
                        self.channel_bus[k].clear()
                        self.channel_bus[k].detect_image = img
                        self.channel_bus[k].oringe_image = img
            for k, output in worker.items():
                try:
                    self.channel_bus[k].faults = output.get()
                except WorkerCrashError as e:
                    # worker 异常: 跳过本帧, 下一帧 init_work 会自动重建 worker
                    print(f'[System][Pipeline] 通道 {k} 检测 worker 异常: {e}, 跳过本帧')
                    self.channel_bus[k].clear()
            if is_exist_fault and self._callback is not None: self._callback()

            # save
            # 如果没有设置批次则不保存
            result = []
            for k, v in self.channel_bus.items():
                info = self.channel_bus[k]
                if len(info.faults) == 0: continue
                result.append(FaultInfo(image=info.detect_image,
                                        faults=info.faults,
                                        location=self.accumulatedDistance(obj='batch'),
                                        batchName=self.batchName(),
                                        worker=self.workerName(),
                                        sampler=k,
                                        camera=k, ))


            return result


        def detect_lightning():
            # 读取结果: 原子地取走事件, 去抖窗口内的连续事件不会被丢弃,
            # 而是等待窗口结束后立即上报, 也不阻塞主循环
            if self.takeLightningEvent():
                self._lightning_pending = True
            result = []
            now = time.time()
            if self._lightning_pending and now >= self._lightning_next_time:
                self._lightning_pending = False
                self._lightning_next_time = now + LIGHTNING_DEBOUNCE
                distance = self.accumulatedDistance(obj='batch')
                self.markLightningReported(distance=distance, active=LIGHTNING_DEBOUNCE)
                result.append(FaultInfo(camera='lightning',
                                        faults=[DetectOutput(0, 0, 0, 0, ftype='针孔缺陷')],
                                        location=distance,
                                        batchName=self.batchName(),
                                        sampler="放电检测",
                                        worker=self.workerName()))
            return result

        while True:
            # ------
            # 是否启动了检测功能
            # ----
            if not self.isDetectEnabled():
                self.setState(state=self.State_DetectDisable)
                time.sleep(0.1)
                continue
            st = time.time()
            # -----  core ----
            result = []
            result += detect_image()
            result += detect_lightning()
            self._last_faults = result
            # 回调
            if len(result) != 0:
                if self._warning_reset is not None and self._warning_reset.is_alive():
                    self._warning_reset.cancel()
                if self.last_warning_time is None or (time.time() - self.last_warning_time) > self.warning_interval:
                    self._io_card.setOutPutData(**{f'ch{self._warning_ch}': 0})
                    self._warning_reset = threading.Timer(self.warning_duration, self._warning_reset_lambda)
                    self._warning_reset.start()
                    self.last_warning_time = time.time()
                self.callback()()


            # 保存
            post_fix = f', 无保存'
            if self.batchName() is not None and self.batchName() != '':
                for f in result: self.save(fault=f)
                post_fix = f', 保存至{self.batchName()}'
            self.setState(state=SettingMixin.State_Normal + post_fix)

            # 如果没有读取到数据,睡眠, 不要阻塞UI线程
            interval = time.time() - st
            if (sleep_time := 0.03 - (interval)) > 0: time.sleep(sleep_time)
            # 记录处理需要的时间, 使用指数平滑
            self._process_time = (self._process_time or interval) * 0.1 + 0.9 * interval

    def _lightning_detect_thread(self):
        while True:
            # ------
            # 是否启动了检测功能
            # ----
            if not self.isDetectEnabled():
                # self.setState(state=self.State_DetectDisable)
                time.sleep(0.1)
                continue
            # 没有启动放电检测, 不用进行读取
            st = time.time()


            # 如果没有读取到数据,睡眠, 不要阻塞UI线程
            if (sleep_time := 0.03 - (time.time() - st)) > 0: time.sleep(sleep_time)

    def accumulatedDistance(self, obj='all') -> float:
        """ 检测的累计距离 """
        # 总的累计距离
        if obj == 'all':
            return VSamplerMixin.accumulatedDistance(self)
        # 只统计当前批次的累计距离
        elif obj == 'batch':
            return VSamplerMixin.accumulatedDistance(self) - self._accumulatedDistance_for_batch
        else:
            raise RuntimeError(f"Not researchable: obj={obj}")

    def processTime(self):
        """ 处理一次需要的时间 """
        return self._process_time or 0

    def pipelineState(self) -> str:
        """ 管线的当前状态 """
        return self._pipeline_state

    def lastFault(self)->Iterable[FaultInfo]:
        return self._last_faults



faultDetectionPipeline = None
faultDetectionPipeline = FaultDetectionPipeline()
