import threading
import time
from functools import lru_cache

import serial

from core._serial import Serial
from ..error import LightSourceControlerSerialConnectError


@lru_cache(maxsize=100)
def commandTamplate(number: int, level: int, closeOther=False, closeFace=False, state=(0, 0, 0, 0)):
    ch = ["A", 'B', "C", "D"]
    if closeOther:
        command = (f'S{ch[0]}{level if number == 0 else 0:0>4}#',
                   f'S{ch[1]}{level if number == 1 else 0:0>4}#',
                   f'S{ch[2]}{level if number == 2 else 0:0>4}#',
                   f'S{ch[3]}{level if number == 3 else 0:0>4}#')

        target = [0, 0, 0, 0]
        target[number] = level
        command = ''.join([c for c, l, s in zip(command, target, state) if l != s])
    elif closeFace:
        target = [0, 0, 0, 0]
        target[number] = level
        target[{0: 1, 1: 0, 2: 3, 3: 2}[number]] = level
        command = ''.join([f'S{ch[i]}{target[i]:0>4}#' for i in range(4)])
    else:
        command = f'S{ch[number]}{level:0>4}#'
    return command.encode('utf8'), tuple(target)

@lru_cache(maxsize=100)
def getLevelTamplate(number: int):
    ch = ["A", 'B', "C", "D"]
    command = f'S{ch[number]}#'
    return command.encode('utf8')

class LightSourceSerial(Serial):
    @classmethod
    def open(cls, port: str, baudrate: int) -> 'Serial':
        _instance = cls()
        # 延时100ms
        _instance.setSerial(serial=serial.Serial(port=port,
                                                 baudrate=baudrate,
                                                 timeout=1))
        return _instance

    def __init__(self, *args, **kwargs):
        self._single_cycle_resolution = None
        self._state = (0, 0, 0, 0)
        self._is_loop = False
        self._group = ((0,), (1,), (2,), (3,))  # 同批次发光的组
        super(LightSourceSerial, self).__init__(*args, **kwargs)

        self._rw_lock = threading.Lock()
        self._close_lock = threading.Lock()


    def setSerial(self, serial: serial.Serial) -> None:
        super(LightSourceSerial, self).setSerial(serial=serial)
        # 检测是否是用于放电检测的串口
        serial.reset_input_buffer()
        serial.write(getLevelTamplate(number=0))
        time.sleep(0.1)
        result = serial.readline().decode()
        if result.startswith('a'):
            pass  # 测试通过
        else:
            raise LightSourceControlerSerialConnectError(f"设备标识为:{result},该串口不能用于光源控制")

    def close(self):
        """ 关闭, 防止线程冲突 """
        # 先关闭循环
        if self._is_loop:
            self._is_loop = False
            time.sleep(0.1)
        with self._close_lock:
            r = super(LightSourceSerial, self).close()
        return r

    def setLightLevel(self, number: int, level: int, closeOther=False, closeFace=False) -> None:
        """
        调整光源的亮度
        :param number: 第几路光源
        :param level:亮度
        :param closeOther:其他路型号自动关闭
        """
        with self._close_lock:
            # print(command)
            if self._serial.isOpen():
                command, state = commandTamplate(number=number, level=level, closeOther=closeOther, closeFace=closeFace,
                                                 state=self._state)
                # self._serial.reset_input_buffer()
                self._serial.write(command)
                self._serial.reset_input_buffer()
                self._state = state

    def getLightLevel(self, number):
        """ get level """
        command = getLevelTamplate(number=number)
        with self._close_lock:
            if self._serial is None or not self._serial.isOpen():
                return None
            self._serial.write(command)
            # 读取控制器返回的亮度值, 不能在读之前清空输入缓冲
            result = self._serial.readline().decode()
        return result