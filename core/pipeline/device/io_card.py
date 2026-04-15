import ctypes
import time
from typing import Callable, List

lib_path = "..\\..\\..\\_rc\\WENYU_EIO16P.dll" if __name__ == "__main__" else "_rc\\WENYU_EIO16P.dll"
lib = ctypes.CDLL(lib_path)  # Windows 用 add.dll

# callback
INTERRUP_CALLBACK = ctypes.CFUNCTYPE(None)

# WY_Open
lib.WY_Open.argtypes = []
lib.WY_Open.restype = ctypes.c_int
# WY_Close
lib.WY_Close.argtypes = []
lib.WY_Close.restype = ctypes.c_int
# int WY_SetOutPutData(int CardNo,unsigned char OutPutData);
lib.WY_SetOutPutData.argtypes = [
    ctypes.c_int,
    ctypes.c_char
]
lib.WY_SetOutPutData.restype = ctypes.c_int
# int WY_GetInPutData (int CardNo,unsigned char &Data);
lib.WY_GetInPutData.argtypes = [
    ctypes.c_int,  # CardNo
    ctypes.POINTER(ctypes.c_ubyte)  # unsigned char*
]
lib.WY_GetInPutData.restype = ctypes.c_int
# int WY_SetInterruptFun(int CardNo, EventInterrupt InterruptFun);
lib.WY_SetInterruptFun.argtypes = [
    ctypes.c_int,
    INTERRUP_CALLBACK]
lib.WY_SetInterruptFun.restype = ctypes.c_int
# int WY_SetInterruptPortEnable(int CardNo, byte RiseEnable, byte FallEnable);
lib.WY_SetInterruptPortEnable.argtypes = [
    ctypes.c_int,  # CardNo
    ctypes.c_ubyte,  # RiseEnable
    ctypes.c_ubyte  # FallEnable
]
lib.WY_SetInterruptPortEnable.restype = ctypes.c_int
# int WY_ResetInterrupt(int CardNo);
lib.WY_ResetInterrupt.argtypes = [
    ctypes.c_int,  # CardNo
]
lib.WY_ResetInterrupt.restype = ctypes.c_int
# int WY_SetInterruptEnable(int CardNo, int Enable);
lib.WY_SetInterruptEnable.argtypes = [
    ctypes.c_int,  # CardNo
    ctypes.c_int,  # enable
]
lib.WY_SetInterruptEnable.restype = ctypes.c_int
# int WY_ClrInterruptRisePort0(int CardNo);
lib.WY_ClrInterruptRisePort0.argtypes = [
    ctypes.c_int,  # CardNo
]
lib.WY_ClrInterruptRisePort0.restype = ctypes.c_int
# int WY_ClrInterruptFallPort0(int CardNo);
lib.WY_ClrInterruptFallPort0.argtypes = [
    ctypes.c_int,  # CardNo
]
lib.WY_ClrInterruptFallPort0.restype = ctypes.c_int


class IOCard():
    WARNING_IDX = 8
    __cards = {}

    @staticmethod
    def to8bit(ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
               ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None,
               revise=False):
        chs = (ch7, ch6, ch5, ch4, ch3, ch2, ch1, ch0)
        if revise:
            string = int("".join(['0' if c == 1 else '1' for c in chs]), 2)
        else:
            string = int("".join([str(c) for c in chs]), 2)
        return string

    @classmethod
    def getCard(cls, number: int) -> 'IOCard':
        if number not in cls.__cards:
            IOCard.open()
            cls.__cards[number] = cls(number=number)
        return cls.__cards[number]

    @classmethod
    def open(self):
        return lib.WY_Open()

    @classmethod
    def close(self):
        return lib.WY_Close()

    def __init__(self, number):
        self._enable = self.open() > number
        # assert self.open() > number
        self._number = number
        self._output_chs = [0, 0, 0, 0, 0, 0, 0, 0]
        self._rise_interrupt_enable = [0, 0, 0, 0, 0, 0, 0, 0]
        self._fall_interrupt_enable = [0, 0, 0, 0, 0, 0, 0, 0]
        self._interrupt_callback_pool: List[Callable] = []
        self.setOutPutData()

        @INTERRUP_CALLBACK
        def _interrupt_callback():
            for c in self._interrupt_callback_pool:
                c()
            lib.WY_ClrInterruptFallPort0(self._number)
            lib.WY_ResetInterrupt(self._number)

        self._interrupt_callback = _interrupt_callback

        lib.WY_SetInterruptEnable(self._number, 1)
        ret = lib.WY_SetInterruptFun(self._number, self._interrupt_callback)
        assert ret == 0, '中断函数设置失败'

    def registerCallback(self, callback: Callable):
        self._interrupt_callback_pool.append(callback)

    def setOutPutData(self,
                      ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                      ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None):
        if not self._enable: return -1
        chs = [c1 if c2 is None else c2 for c1, c2 in zip(self._output_chs, (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7,))]
        self._output_chs = chs
        string = self.to8bit(*chs, revise=True)
        ret = lib.WY_SetOutPutData(self._number, string)
        assert ret == 0, 'ret'
        return ret

    def getInputData(self):
        data = ctypes.c_ubyte()  # 分配 1 字节
        ret = lib.WY_GetInPutData(self._number, ctypes.byref(data))
        assert ret == 0
        mask = data.value
        return [(mask >> i) & 1 for i in range(8)]

    def setRiseInterrupEnbale(self, ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                              ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None):
        enable = [c1 if c2 is None else c2 for c1, c2 in zip(self._rise_interrupt_enable,
                                                             (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7,))]
        self._rise_interrupt_enable = enable
        ret = lib.WY_SetInterruptPortEnable(self._number,
                                            self.to8bit(*self._rise_interrupt_enable, revise=False),
                                            self.to8bit(*self._fall_interrupt_enable, revise=False), )
        assert ret == 0

    def setFallInterrupEnbale(self, ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                              ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None):
        enable = [c1 if c2 is None else c2 for c1, c2 in zip(self._fall_interrupt_enable,
                                                             (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7,))]
        self._fall_interrupt_enable = enable
        ret = lib.WY_SetInterruptPortEnable(self._number,
                                            self.to8bit(*self._rise_interrupt_enable, revise=False),
                                            self.to8bit(*self._fall_interrupt_enable, revise=False), )


if __name__ == "__main__":
    # 打开 IO card
    card_num = IOCard.open()
    print(f'卡片数量:{card_num}')

    card = IOCard(0)

    for _ in range(1000):
        time.sleep(2)
        card.setOutPutData(ch0=1, ch1=1, ch2=0, ch3=0, ch4=1, ch5=1, ch6=1, ch7=1)
        print(1)
        time.sleep(2)
        print(2)
        card.setOutPutData(ch0=0, ch1=0, ch2=1, ch3=1, ch4=0, ch5=0, ch6=0, ch7=0)
