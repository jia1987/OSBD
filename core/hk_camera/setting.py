# -*- coding: utf-8 -*-
from ..HK_MvImport.MvCameraControl_class import *
from ..HK_MvImport.MvErrorDefine_const import *
from ..HK_MvImport.CameraParams_header import *
from .utils import To_hex_str


class CameraSettingMixin(object):
    _camera: MvCamera

    def setExposure(self, exposureTime: int):
        assert isinstance(exposureTime, int), 'the time of exposure must be int'
        ret = self._camera.MV_CC_SetEnumValue("ExposureAuto", 0)
        ret = self._camera.MV_CC_SetFloatValue("ExposureTime", float(exposureTime))
        if ret != 0:
            raise RuntimeError('show error', 'set exposure time fail! ret = ' + To_hex_str(ret))

    def setGain(self, gain: float):
        ret = self._camera.MV_CC_SetFloatValue("Gain", float(gain))
        if ret != 0:
            raise RuntimeError('show error', 'set gain fail! ret = ' + To_hex_str(ret))

    def setFrameRate(self, frameRate: int):
        ret = self._camera.MV_CC_SetFloatValue("AcquisitionFrameRate", float(frameRate))
        if ret != 0:
            raise RuntimeError('show error', 'set acquistion frame rate fail! ret = ' + To_hex_str(ret))