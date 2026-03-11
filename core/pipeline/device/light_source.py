import threading
import time
from functools import lru_cache

import serial
from typing import Callable, Optional

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

@lru_cache(maxsize=100)
def switchamplate(ch1: bool, ch2: bool, ch3: bool, ch4: bool):
    """开关光源 (响应速度优先)"""
    ch1 = "1" if ch1 else "0"
    ch2 = "1" if ch2 else "0"
    ch3 = "1" if ch3 else "0"
    ch4 = "1" if ch4 else "0"
    return f'switch({ch1},{ch2},{ch3},{ch4})\n'.encode()


class LightSourceSerial_(Serial):
    def __init__(self, *args, **kwargs):
        self._single_cycle_resolution = None
        self._state = (0, 0, 0, 0)
        self._is_loop = False
        self._group = ((0,), (1,), (2,), (3,))  # 同批次发光的组
        super(LightSourceSerial, self).__init__(*args, **kwargs)

        self._rw_lock = threading.Lock()
        self._close_lock = threading.Lock()
        self.ch_lock = (threading.Lock(), threading.Lock(), threading.Lock(), threading.Lock())

    def setSerial(self, serial: serial.Serial) -> None:
        super(LightSourceSerial, self).setSerial(serial=serial)
        # 检测是否是用于放电检测的串口
        serial.reset_input_buffer()
        serial.write('machine()\n'.encode())
        time.sleep(0.1)
        result = serial.readline().decode()
        if result.startswith('Light-Source-Pico'):
            pass  # 测试通过
        else:
            raise LightSourceControlerSerialConnectError(f"设备标识为:{result},该串口不能用于光源控制")

    def setGroup(self, ch1: str, ch2: str, ch3: str, ch4: str) -> None:
        """ 自动优化批次, 让一次循环可以尽量多的光源 """
        tags = (ch1, ch2, ch3, ch4)
        min_tag = tuple({ch1, ch2, ch3, ch4})
        self._group = tuple(tuple(i for i, t in enumerate(tags) if mt == t) for mt in min_tag)

    def close(self):
        """ 关闭, 防止线程冲突 """
        # 先关闭循环
        if self._is_loop:
            self._is_loop = False
            time.sleep(0.1)
        with self._close_lock:
            r = super(LightSourceSerial, self).close()
            for lock in self.ch_lock:
                if lock.locked():
                    lock.release()
        return r

    def startLoop(self, callback: Optional[Callable] = None):
        """启动循环"""
        self._t = threading.Thread(target=self.loop)
        self._t.daemon = True
        self._is_loop = True
        self._callback = callback
        self._t.start()

    def loop(self):
        """循环屏闪"""

        def release(idx):
            if self.ch_lock[idx].locked():
                self.ch_lock[idx].release()

        # 全部上锁, 只有亮才解锁
        for lock in self.ch_lock:
            lock.acquire()
        # ============= 频闪 ==============
        # 使用switch进行频闪, 这样的响应速度最快
        # 1.光源开关
        # 2.释放线程锁, 让摄像头读取线程更新图片
        # ================================
        while self._serial.isOpen() and self._is_loop:
            for g in self._group:
                # self.switch(ch1=0 in g, ch2=1 in g, ch3=2 in g, ch4=3 in g, )
                time.sleep(0.0333)
                # for i in g: release(i)
                if self._callback is not None: self._callback(ch1=0 in g, ch2=1 in g, ch3=2 in g, ch4=3 in g)
                # time.sleep(0.03)  # 释放锁,让其他线程有时间接管程序
                # for i in g: self.ch_lock[i].acquire()

    def switch(self, ch1: bool, ch2: bool, ch3: bool, ch4: bool):
        """开关光源 (响应速度优先)"""
        s = switchamplate(ch1=ch1, ch2=ch2, ch3=ch3, ch4=ch4)

        self._serial.write(s)
        while self._serial.out_waiting > 0:
            time.sleep(0.001)

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
        self._serial.write(command)
        self._serial.reset_input_buffer()
        result = serial.readline().decode()
        return result