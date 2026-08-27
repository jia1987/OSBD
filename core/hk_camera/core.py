import threading
import time

import numpy as np

from ..HK_MvImport.MvCameraControl_class import *
from ..HK_MvImport.CameraParams_header import *

ret = MvCamera.MV_CC_Initialize()
if ret != 0:
    raise RuntimeError(f'初始化SDK失败，错误码: {ret}')

from .tools import CameraToolsMixin
from ._io import CameraIOMixin
from .setting import CameraSettingMixin
from .error import CameraInitError

import numpy as np
from PIL import Image
from ..HK_MvImport.MvCameraControl_class import *
from ..HK_MvImport.CameraParams_header import *
from .CamOperation_class import CameraOperation
from .error import CameraReadError

# _img = Image.open(r'img.png').convert('L')
# _img = np.array(_img)[:, :].astype(np.uint8)
class Camera(CameraToolsMixin, CameraIOMixin, CameraSettingMixin):

    def __init__(self, port, device_list=None):
        self._camera = MvCamera()
        self._cache: np.ndarray = None
        CameraIOMixin.__init__(self)
        device_list = device_list or self.device_list()
        self.op = CameraOperation(obj_cam=self._camera, st_device_list=device_list)

        # 通过 SDK 寻找设备
        device_enum = self.enum_devices()
        if port not in device_enum:
            raise CameraInitError("Not found devices")
        idx = self.enum_devices().index(port)

        # 枚举设备
        stDeviceList = cast(device_list.pDeviceInfo[idx], POINTER(MV_CC_DEVICE_INFO)).contents
        ret = self._camera.MV_CC_CreateHandle(stDeviceList)
        # 打开设备（使用已创建的句柄）
        ret = self._camera.MV_CC_OpenDevice()

        if ret != 0:
            raise RuntimeError(f"打开设备失败，错误码: {ret}")
        self.device_parameters()

        # 启动读取线程, 异步读取
        self._running = True
        self._thread = threading.Thread(target=self._read_thread)
        self._thread.daemon = True
        self._thread.start()
        self.op.b_open_device = True

    def device_parameters(self):
        # 获取相机参数
        width = c_uint()
        height = c_uint()
        pixel_format = c_uint()
        payload_size = c_uint()
        stParam = MVCC_INTVALUE()
        camera = self._camera

        ret = camera.MV_CC_GetIntValue("PayloadSize", stParam)
        if ret != 0:
            raise RuntimeError(f"获取PayloadSize失败，错误码: {ret}")

        payload_size.value = stParam.nCurValue

        # 获取宽度
        ret = camera.MV_CC_GetIntValue("Width", stParam)
        if ret != 0:
            raise RuntimeError(f"获取宽度失败，错误码: {ret}")
        width.value = stParam.nCurValue

        # 获取高度
        ret = camera.MV_CC_GetIntValue("Height", stParam)
        if ret != 0:
            raise RuntimeError(f"获取高度失败，错误码: {ret}")

        height.value = stParam.nCurValue

        pixel_format.value = 17301505  # RGB8
        # 或
        # pixel_format.value = 17301514  # Mono8

        # 曝光时间
        exposure_time = 15000  # 单位：微秒
        ret = camera.MV_CC_SetFloatValue("ExposureTime", exposure_time)

        # 开始抓图
        ret = camera.MV_CC_StartGrabbing()
        if ret != 0:
            raise RuntimeError(f"开始抓图失败，错误码: {ret}")

        # 分配缓冲区
        data_buf = (c_ubyte * payload_size.value)()
        data_size = c_uint(payload_size.value)

        stFrameInfo = MV_FRAME_OUT_INFO_EX()

        data_buf = (c_ubyte * payload_size.value)()
        ret = camera.MV_CC_GetOneFrameTimeout(
            byref(data_buf),
            payload_size.value,
            stFrameInfo,
            1000
        )

        self._stFrameInfo = stFrameInfo
        self._payload_size = payload_size

    def close(self) -> None:
        """ close camera """
        # 先停止读线程, 避免 close 后取帧报错导致空转
        self._running = False
        try:
            self._camera.MV_CC_StopGrabbing()
        except Exception:
            pass
        return self._camera.MV_CC_CloseDevice()

    def _read_thread(self):
        while self._running:
            try:
                frame = self._read()
                # _read() 返回的是复用缓冲区的视图, 必须拷贝一份,
                # 否则下一帧会原地覆盖已被上层(显示/保存)持有的数据
                self._cache = frame.copy()
            except CameraReadError as e:
                # 取帧失败(超时等)稍后重试, 不能无睡眠空转
                if self._running:
                    time.sleep(0.01)
            except Exception as e:
                # 设备关闭等非预期异常: 未关闭则抛出, 已关闭则退出线程
                if not self._running:
                    break
                raise e

    def width(self):
        return self._stFrameInfo.width

    def height(self):
        return self._stFrameInfo.height

    def read(self) -> np.ndarray or None:
        return self._cache


__all__ = (
    'MvCamera'
)
