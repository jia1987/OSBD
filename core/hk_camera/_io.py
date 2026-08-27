import numpy as np

from .error import CameraReadError
from ..HK_MvImport.CameraParams_header import *
from ..HK_MvImport.MvCameraControl_class import *


class CameraIOMixin(object):
    _camera: MvCamera
    _stFrameInfo: MV_FRAME_OUT_INFO_EX
    _payload_size: c_uint

    def __init__(self):
        # 创建一个buff作为读取的缓存区, 避免频繁创建
        self._data_buf = None
        self._fram: np.ndarray = None

    def read_buff(self):
        """ 从buff中读取数据, 不负责解码"""
        stFrameInfo = self._stFrameInfo
        payload_size = self._payload_size
        # 避免频繁的创建
        if self._data_buf is None:
            self._data_buf = (c_ubyte * payload_size.value)()
            self._frame = np.frombuffer(self._data_buf, dtype=np.uint8)
        data_buf = self._data_buf
        ret = self._camera.MV_CC_GetOneFrameTimeout(
            # ret = self._camera.MV_CC_GetImageForBGR(
            byref(data_buf),
            payload_size.value,
            stFrameInfo,
            1000
        )
        return ret, data_buf

    def _read(self) -> np.ndarray:
        stFrameInfo = self._stFrameInfo
        payload_size = self._payload_size

        ret, data_buf = self.read_buff()

        if ret == 0:
            frame = self._frame  # 直接缓存中读取
            actual_width = stFrameInfo.nWidth
            actual_height = stFrameInfo.nHeight

            if stFrameInfo.enPixelType == 17301505:  # RGB8
                # RGB8 每像素 3 字节
                expected_size = actual_width * actual_height * 3
                if len(frame) < expected_size:
                    raise RuntimeError(f"数据大小不匹配: 期望 {expected_size}, 实际 {len(frame)}")

                frame = frame[:expected_size].reshape((actual_height, actual_width, 3))
            elif stFrameInfo.enPixelType == 17301514:  # Mono8
                expected_size = actual_width * actual_height
                if len(frame) != expected_size:
                    raise RuntimeError(f"数据大小不匹配: 期望 {expected_size}, 实际 {len(frame)}")

                frame = frame.reshape((actual_height, actual_width))
            elif stFrameInfo.enPixelType == 17301513:  # 可能是 Bayer 格式
                expected_size = actual_width * actual_height
                if len(frame) != expected_size:
                    raise RuntimeError(f"数据大小不匹配: 期望 {expected_size}, 实际 {len(frame)}")

                frame = frame.reshape((actual_height, actual_width))
            else:
                raise RuntimeError(f"不支持的像素格式: {stFrameInfo.enPixelType}")
        else:
            raise CameraReadError(f"获取图像失败，错误码: {ret}")
        return frame
