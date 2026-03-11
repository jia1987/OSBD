class DeviceConnectError(Exception):
    """ 设备链接错误 """


class CameraConnectError(DeviceConnectError):
    """ 摄像头链接错误"""


class OpencvCameraConnectError(CameraConnectError):
    """ Hk摄像头链接错误"""


class HKCameraConnectError(CameraConnectError):
    """ Hk摄像头链接错误"""


class SerialConnectError(DeviceConnectError):
    """ 串口设备链接错误 """


class LightningSerialConnectError(SerialConnectError):
    """ 放电检测串口链接错误 """


class LightSourceControlerSerialConnectError(SerialConnectError):
    """ 光源控制器串口链接错误 """


class VSamplerSerialConnectError(SerialConnectError):
    """ 计米轮串口链接错误 """
