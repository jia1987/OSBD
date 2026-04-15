import threading
import time

from typing import Dict

from .device import LightSourceSerial, IOCard
from .device.camera import Camera, HK_Camera
from .error import CameraConnectError
from .meta import ChannelInfo, ModelConfig, PipelineType
from ..config import config


class ChannelInfo(ChannelInfo):
    def __init__(self, *args,
                 pipeline, cameras: Dict[str, Camera], ctx: str,
                 **kwargs):
        super(ChannelInfo, self).__init__(*args, **kwargs)
        self._pipeline = pipeline
        self._ctx: str = ctx
        self._cameras: Dict[str, Camera] = cameras

    @property
    def camera(self) -> Camera:
        """ 摄像头 """
        mc: ModelConfig = self._pipeline.modelConfig()
        if mc is None:
            camera_ctx = {i2: i1 for i1, i2 in zip(PipelineType.CAMERAS, PipelineType.CHANNELS)}[self._ctx]
        else:
            camera_ctx = mc.mapper[self._ctx]
        return self._cameras.get(camera_ctx, None)


class CameraMixin():
    def __init__(self):
        # 可有的摄像头示例 (物理摄像头)
        self._cameras: Dict[str, Camera] = {}
        # 通道信息
        # 四个通道信息, 可以使用不同或相同的摄像头
        self.channel_bus = {ctx: ChannelInfo(pipeline=self,
                                             cameras=self._cameras,
                                             ctx=ctx) for ctx in PipelineType.CHANNELS}
        # 光源控制串口
        self._light_source: LightSourceSerial = None
        # pice io card, 控制光源和相机触发
        self._io_card = IOCard.getCard(number=0)
        # 摄像头是否使能
        self._is_camera_enabled = False
        # 光源循环的组
        self._light_group = ((0,), (1,), (2,), (3,))
        # 光源循环的线程
        self._light_loop_thread = threading.Thread(target=self._light_loop_thread_func)
        self._light_loop_thread.daemon = True
        self._light_loop_thread.start()

    def setCameraEnabled(self, enabled: bool) -> None:
        """ 使能摄像头 """
        if enabled:
            device_list = HK_Camera.device_list()
            self._cameras.clear()
            for number, (k, port, exposure) in enumerate(zip(
                    PipelineType.CAMERAS,
                    config.get(config.Camera_Prots),
                    config.get(config.Camera_Exposures))):
                # inti camera
                try:
                    camera = Camera(read_mode=config.get(config.Camera_ReadModes)[number],
                                    img_path=config.get(config.Camera_Imgs)[number],
                                    video_path=config.get(config.Camera_Videos)[number],
                                    exposureTime=exposure,
                                    port=port,
                                    device_list=device_list)
                    self._cameras[k] = camera
                except CameraConnectError:
                    self._cameras[k] = None
                    print(f"[System] {k}: Connect failed...")
                    continue
                except Exception as e:
                    raise e

                # 如果启动了光源控制器
                # 将摄像头改为触发模式
                camera.setTrigger(isTrigger=self._light_source is not None)
                # camera.op.Set_trigger_mode(self._light_source is not None)
                print(f"[System] {k}: Connect successfully...")
        else:
            for ctx in [k for k, c in self._cameras.items() if c is not None]:
                self._cameras[ctx].close()
                self._cameras[ctx] = None
                print(f"[System] Camera: Disconnect...")

        self._is_camera_enabled = enabled

    def setLightSourceEnable(self, enable: bool):
        """
        设置光源使能
        :param enable: 使能
        """
        if enable:
            baudrate = int(config.get(config.LightSource_Baudrate))
            port = str(config.get(config.LightSource_Port))
            print(f"[System] Connect Light Source (Baudrate:{baudrate}, Port:{port})...")
            self._light_source: LightSourceSerial = LightSourceSerial.open(baudrate=baudrate, port=port)
            # 更新光源控制器的曝光组
            modelconfig = self.modelConfig()
            if modelconfig:
                self.setLightGroup(*(modelconfig.exposureBatch[ctx] for ctx in PipelineType.CAMERA_LIST))
        else:
            print(f"[System] Disconnect Light Source...")
            self._light_source.close()
            self._light_source = None
        # 同步到相机
        for number, camera in self._cameras.items():
            if camera is None: continue
            camera.setTrigger(isTrigger=self._light_source is not None)

    def setLightGroup(self, ch1: str, ch2: str, ch3: str, ch4: str) -> None:
        """ 自动优化批次, 让一次循环可以尽量多的光源 """
        tags = (ch1, ch2, ch3, ch4)
        min_tag = tuple({ch1, ch2, ch3, ch4})
        self._light_group = tuple(tuple(i for i, t in enumerate(tags) if mt == t) for mt in min_tag)

    def _light_loop_thread_func(self):
        """ 当相机启动频闪, 触发对应的摄像头 """
        while True:
            if not self.isLightSourceEnabled():
                time.sleep(1)
                continue
            for g in self._light_group:
                chs = (0 in g, 1 in g, 2 in g, 3 in g)
                chs = tuple(1 if not c else 0 for c in chs)
                self._io_card.setOutPutData(*chs, *chs)
                time.sleep(0.033333)

    def channels(self, ctx: str) -> ChannelInfo:
        return self.channel_bus.get(ctx)

    def isCameraEnabled(self) -> bool:
        """ return True if camera is enabled """
        return self._is_camera_enabled

    def isLightSourceEnabled(self) -> bool:
        """ 光源是否使能 """
        return self._light_source is not None

    def IOCard(self)->IOCard:
        return self._io_card