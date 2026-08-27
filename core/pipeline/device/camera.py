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
    """ 普通摄像头 (OpenCV VideoCapture) """

    def __init__(self, idx: int):
        cap = cv2.VideoCapture(idx)

        if not cap.isOpened():
            cap.release()
            raise OpencvCameraConnectError(f"摄像头 {idx} 打开失败")
        self._cap = cap

    def read(self):
        ret, frame = self._cap.read()
        if not ret or frame is None:
            raise OpencvCameraConnectError("摄像头读取帧失败")
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

    def close(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None


class VedioCamera(CameraAbstract):
    """ 视频文件输入 (演示/验收用) """

    def __init__(self, path: str):
        cap = cv2.VideoCapture()
        cap.open(path, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            cap.release()
            raise OpencvCameraConnectError(f"视频 {path} 打开失败")
        self._cap = cap

    def read(self):
        ret, frame = self._cap.read()
        if not ret or frame is None:
            # 视频播放结束, 循环播放
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
            if not ret or frame is None:
                raise OpencvCameraConnectError("视频读取帧失败")
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

    def close(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None


class ImageCamera(CameraAbstract):
    """ 静态图片输入 (无硬件演示/验收用) """

    def __init__(self, path: str):
        if not path or not os.path.exists(path):
            raise OpencvCameraConnectError(f"图片不存在: {path}")
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            raise OpencvCameraConnectError(f"图片解码失败: {path}")
        self._img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def read(self):
        return self._img


class Camera():
    ReadMode_Hk = 'Mode_Hk'
    ReadMode_Capture = 'Mode_Capture'
    ReadMode_Vedio = 'Mode_Vedio'
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
        else:
            raise OpencvCameraConnectError(f"未知的相机读取模式: {read_mode}")

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
