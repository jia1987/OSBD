import sys
import warnings
from typing import List
from .CamOperation_class import CameraOperation
from core.HK_MvImport.MvCameraControl_class import *
from core.HK_MvImport.MvErrorDefine_const import *
from core.HK_MvImport.CameraParams_header import *
# from PyUICBasicDemo import Ui_MainWindow
# -*- coding: utf-8 -*-
import sys
from ..HK_MvImport.MvCameraControl_class import *
from ..HK_MvImport.MvErrorDefine_const import *
from ..HK_MvImport.CameraParams_header import *


class CameraToolsMixin(object):
    @staticmethod
    def decoding_char(c_ubyte_value):
        c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
        try:
            decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
        except UnicodeDecodeError:
            decode_str = str(c_char_p_value.value)
        return decode_str

    @classmethod
    def device_list(cls):
        deviceList = MV_CC_DEVICE_INFO_LIST()
        n_layer_type = MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
        ret = MvCamera.MV_CC_EnumDevices(n_layer_type, deviceList)
        return deviceList

    @classmethod
    def enum_devices(cls, show=False) -> List[str]:
        global deviceList
        global obj_cam_operation

        deviceList = MV_CC_DEVICE_INFO_LIST()
        n_layer_type = (MV_GIGE_DEVICE | MV_USB_DEVICE | MV_GENTL_CAMERALINK_DEVICE
                        | MV_GENTL_CXP_DEVICE | MV_GENTL_XOF_DEVICE)
        ret = MvCamera.MV_CC_EnumDevices(n_layer_type, deviceList)
        if ret != 0:
            # strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            # return ret
            raise RuntimeError()

        if deviceList.nDeviceNum == 0:
            # QMessageBox.warning(mainWindow, "Info", "Find no device", QMessageBox.Ok)
            # return ret
            warnings.warn('Not found device')
            return []
        if show: print("Find %d devices!" % deviceList.nDeviceNum)

        devList = []
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE or mvcc_dev_info.nTLayerType == MV_GENTL_GIGE_DEVICE:
                if show: print("\ngige device: [%d]" % i)
                user_defined_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                if show: print("device user define name: " + user_defined_name)
                if show: print("device model name: " + model_name)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                if show: print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                if show: print("\nu3v device: [%d]" % i)
                user_defined_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                if show: print("device user define name: " + user_defined_name)
                if show: print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                if show: print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
            elif mvcc_dev_info.nTLayerType == MV_GENTL_CAMERALINK_DEVICE:
                if show: print("\nCML device: [%d]" % i)
                user_defined_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stCMLInfo.chUserDefinedName)
                model_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stCMLInfo.chModelName)
                if show: print("device user define name: " + user_defined_name)
                if show: print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stCMLInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                if show: print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]CML: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
            elif mvcc_dev_info.nTLayerType == MV_GENTL_CXP_DEVICE:
                if show: print("\nCXP device: [%d]" % i)
                user_defined_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stCXPInfo.chUserDefinedName)
                model_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stCXPInfo.chModelName)
                if show: print("device user define name: " + user_defined_name)
                if show: print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stCXPInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                if show: print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]CXP: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
            elif mvcc_dev_info.nTLayerType == MV_GENTL_XOF_DEVICE:
                if show: print("\nXoF device: [%d]" % i)
                user_defined_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stXoFInfo.chUserDefinedName)
                model_name = cls.decoding_char(mvcc_dev_info.SpecialInfo.stXoFInfo.chModelName)
                if show: print("device user define name: " + user_defined_name)
                if show: print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stXoFInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                if show: print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]XoF: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")

        return devList
