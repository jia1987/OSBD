import serial
import serial.tools.list_ports
from dataclasses import dataclass

# 串口默认读取超时(秒): 设备不响应时读取会返回而不是永久阻塞
DEFAULT_TIMEOUT = 1


@dataclass
class Post():
    pass


class Serial():
    @staticmethod
    def posts():
        # 获取所有串口设备实例。
        # 如果没找到串口设备，则输出：“无串口设备。”
        # 如果找到串口设备，则依次输出每个设备对应的串口号和描述信息。
        ports_list = list(serial.tools.list_ports.comports())
        return ports_list

    @classmethod
    def open(cls, port: str, baudrate: int, timeout: float = DEFAULT_TIMEOUT) -> 'Serial':
        _instance = cls()
        _instance.setSerial(serial=serial.Serial(port=port,
                                                 baudrate=baudrate,
                                                 timeout=timeout, ))
        return _instance

    @staticmethod
    def hex2int(string, bin=16, signed=False):
        if signed:
            """把任意长度的十六进制字符串转为有符号整数"""
            dec_num = int(string, 16)
            m = 16 ** len(string)
            mid = m // 2 - 1
            if dec_num > mid:
                dec_num = dec_num - 16 ** len(string)
            val = dec_num
        else:
            val = int(string, bin)
        return val

    def __init__(self):
        self._serial:serial.Serial = None

    def setSerial(self, serial: serial.Serial) -> None:
        self._serial = serial

    def close(self):
        if self._serial is not None:
            self._serial.close()

    def read(self):
        return self._serial.read()

    def isOpen(self) -> bool:
        return self._serial is not None and self._serial.is_open
