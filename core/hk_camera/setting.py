import sys
import warnings
import time
from typing import List
from .CamOperation_class import CameraOperation
from ..HK_MvImport.MvCameraControl_class import *
from ..HK_MvImport.MvErrorDefine_const import *
from ..HK_MvImport.CameraParams_header import *
# from PyUICBasicDemo import Ui_MainWindow
# -*- coding: utf-8 -*-
import sys
from ..HK_MvImport.MvCameraControl_class import *
from ..HK_MvImport.MvErrorDefine_const import *
from ..HK_MvImport.CameraParams_header import *
from .utils import To_hex_str


class CameraSettingMixin(object):
    _camera: MvCamera

    def setExposure(self, exposureTime: int):
        assert isinstance(exposureTime, int), 'the time of exposure must be int'
        ret = self._camera.MV_CC_SetEnumValue("ExposureAuto", 0)
        time.sleep(0.2)
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

        # ch:设置触发模式 | en:set trigger mode

    def set_continue_mode(self):
        """ch:设置触发模式 | en:set trigger mode"""
        ret = obj_cam_operation.Set_trigger_mode(False)
        if ret != 0:
            strError = "Set continue mode failed ret:" + ToHexStr(ret) + " mode is " + str(is_trigger_mode)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            ui.radioContinueMode.setChecked(True)
            ui.radioTriggerMode.setChecked(False)
            ui.bnSoftwareTrigger.setEnabled(False)


    def set_software_trigger_mode(self):
        """ ch:设置软触发模式 | en:set software trigger mode """
        ret = obj_cam_operation.Set_trigger_mode(True)
        if ret != 0:
            strError = "Set trigger mode failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        else:
            ui.radioContinueMode.setChecked(False)
            ui.radioTriggerMode.setChecked(True)
            ui.bnSoftwareTrigger.setEnabled(isGrabbing)

        # ch:设置触发命令 | en:set trigger software

    def trigger_once(self):
        ret = obj_cam_operation.Trigger_once()
        if ret != 0:
            strError = "TriggerSoftware failed ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)