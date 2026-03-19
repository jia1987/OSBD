import cv2
import numpy as np
import os
from ..error import OpencvCameraConnectError
from ...HK_MvImport.MvCameraControl_class import MV_TRIGGER_MODE_OFF, MV_TRIGGER_SOURCE_LINE0,MV_TRIGGER_MODE_ON
from ...hk_camera import Camera as HK_Camera


class HKCamera(HK_Camera):
    def __init__(self, **kwargs):
        self._isTrigger = False
        super(HKCamera, self).__init__(**kwargs)

    def setTrigger(self, isTrigger: bool):
        """ 设置触发模式 """
        if not isTrigger:
            self.op.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        else:
            self.op.obj_cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_ON)
            self.op.obj_cam.MV_CC_SetEnumValue("TriggerSource", MV_TRIGGER_SOURCE_LINE0)
        self._isTrigger = isTrigger

    def trigger(self) -> None:
        """ 触发 """
        # self.trigger_once()

    # def read_buff(self):
    #     """ internal function: read a frame"""
    #     # 考虑光源, 要加读取锁防止同时启动光源
    #     if self._isTrigger:
    #         stOutFrame = MV_FRAME_OUT()
    #         memset(byref(stOutFrame), 0, sizeof(stOutFrame))
    #         self.st_frame_info = stOutFrame.stFrameInfo
    #         with self.read_thread_lock:
    #             # 使用触发将新的图像保存到buffer中
    #             ret = self.op.Trigger_once()
    #         self.read_thread_lock.acquire()  # <--进入等待状态
    #
    #         ret = self._camera.MV_CC_GetImageBuffer(stOutFrame, 1000)
    #         buf_save_image = (c_ubyte * stOutFrame.stFrameInfo.nFrameLen)()
    #         cdll.msvcrt.memcpy(byref(buf_save_image), stOutFrame.pBufAddr, self.st_frame_info.nFrameLen)
    #         self._frame = np.frombuffer(buf_save_image, dtype=np.uint8)
    #         buffer = buf_save_image
    #         self._camera.MV_CC_FreeImageBuffer(stOutFrame)
    #     else:
    #         ret, buffer = super(HK_Camera, self).read_buff()
    #     return ret, buffer


class CameraAbstract():
    _isTrigger = False

    def setExposure(self, exposure: int):
        pass

    def setTrigger(self, isTrigger: bool):
        """ 设置触发模式 """
        self._isTrigger = isTrigger

    def trigger(self) -> None:
        """ 触发 """
        pass

    def isTrigger(self):
        return self._isTrigger

    def close(self):
        pass


class CaptrueCamera(CameraAbstract):
    def __init__(self, idx: int):
        cap = cv2.Capture(idx)

        if not cap.isOpened():
            raise OpencvCameraConnectError("摄像头path打开失败")


class VedioCamera(CameraAbstract):
    def __init__(self, path: str):
        cap = cv2.VideoCapture()
        cap.open(path, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            raise OpencvCameraConnectError("摄像头path打开失败")


class ImageCamera(CameraAbstract):
    def __init__(self, path: str):
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        self._img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.basename(path), self._img)

    def read(self):
        return self._img


class Camera():
    ReadMode_Hk = 'Mode_Hk'
    ReadMode_Capture = 'ReadMode_Capture'
    ReadMode_Vedio = 'ReadMode_OpenCV'
    ReadMode_Img = 'Mode_img'

    @classmethod
    def HK_deivces(cls):
        """ get all HK camera deivces"""
        return HK_Camera.enum_devices()

    def __init__(self,
                 port=None,
                 capture=None,
                 device_list=None,
                 img_path=None,
                 video_path=None,
                 exposureTime=None,
                 read_mode=ReadMode_Hk):

        if read_mode == self.ReadMode_Hk:
            self._capture = HKCamera(port=port, device_list=device_list)
            if exposureTime:
                self._capture.setExposure(exposureTime=exposureTime)
        elif read_mode == self.ReadMode_Capture:
            self._capture = CaptrueCamera(idx=capture)
        elif read_mode == self.ReadMode_Vedio:
            self._capture = VedioCamera(path=video_path)
        elif read_mode == self.ReadMode_Img:
            self._capture = ImageCamera(path=img_path)

    def read(self):
        """ get a frame"""
        return self._capture.read()

    def setExposure(self, exposure: int) -> None:
        """ set exposure """
        self._capture.setExposure(exposure)

    def setTrigger(self, isTrigger: bool):
        self._capture.setTrigger(isTrigger=isTrigger)

    def trigger(self) -> None:
        self._capture.trigger()

    def isTrigger(self) -> bool:
        return self._capture.isTrigger()

    def close(self):
        return self._capture.close()
