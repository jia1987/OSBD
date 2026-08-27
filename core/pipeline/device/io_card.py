import ctypes
import time
from typing import Callable, List, Optional

lib_path = "..\\..\\..\\_rc\\WENYU_EIO16P.dll" if __name__ == "__main__" else "_rc\\WENYU_EIO16P.dll"


def _load_lib():
    """ 加载 IO 卡 DLL.

    没有 DLL / 没有 IO 卡时程序应能继续启动(无硬件冒烟测试),
    因此这里不抛异常, 返回 None 表示硬件不可用.
    """
    try:
        return ctypes.CDLL(lib_path)
    except OSError as e:
        print(f'[System][IOCard] 加载 {lib_path} 失败, IO 卡功能不可用: {e}')
        return None


lib = _load_lib()

if lib is not None:
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
        ctypes.c_ubyte
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
else:
    INTERRUP_CALLBACK = None


class IOCard():
    # 注意: WENYU_EIO16P 卡物理上只有 8 路输出 (ch0~ch7),
    # WY_SetOutPutData 一次只写 1 字节. 声光报警等逻辑通道
    # 必须映射到 ch0~ch7 之一 (见 core.config.IOCard_WarningChannel).
    WARNING_IDX = 8
    __cards = {}

    @staticmethod
    def to16bit(ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None,
                ch8: int = None, ch9: int = None, ch10: int = None, ch11: int = None,
                ch12: int = None, ch13: int = None, ch14: int = None, ch15: int = None,
                revise=False):
        chs = (ch15, ch14, ch13, ch12, ch11, ch10, ch9, ch8, ch7, ch6, ch5, ch4, ch3, ch2, ch1, ch0)
        if revise:
            string = int("".join(['0' if c == 1 else '1' for c in chs]), 2)
        else:
            string = int("".join([str(c) for c in chs]), 2)
        return string

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
        if lib is None:
            return 0
        ret = lib.WY_Open()
        return ret if ret >= 0 else 0

    @classmethod
    def close(self):
        if lib is None:
            return -1
        return lib.WY_Close()

    def __init__(self, number):
        self._number = number
        self._enable = lib is not None and self.open() > number
        if not self._enable:
            print(f'[System][IOCard] 未检测到 IO 卡(编号 {number}), 相关硬件功能(光源触发/放电输入/报警输出)不可用')
        self._output_chs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._rise_interrupt_enable = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._fall_interrupt_enable = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._interrupt_callback_pool: List[Callable] = []
        self._interrupt_callback: Optional[object] = None
        if self.setOutPutData() != 0:
            # 初始化输出失败不影响启动
            print('[System][IOCard] 初始化输出失败')

        if self._enable:
            @INTERRUP_CALLBACK
            def _interrupt_callback():
                # 该回调运行于 C 中断线程, 任何异常都不允许抛到 ctypes 之外,
                # 否则是未定义行为(可能直接进程崩溃)
                for c in self._interrupt_callback_pool:
                    try:
                        c()
                    except Exception as e:
                        print(f'[System][IOCard] 中断回调执行失败: {e}')
                try:
                    lib.WY_ClrInterruptFallPort0(self._number)
                    lib.WY_ResetInterrupt(self._number)
                except Exception as e:
                    print(f'[System][IOCard] 中断复位失败: {e}')

            self._interrupt_callback = _interrupt_callback

            lib.WY_SetInterruptEnable(self._number, 1)
            ret = lib.WY_SetInterruptFun(self._number, self._interrupt_callback)
            if ret != 0:
                # 无卡/驱动异常时降级, 而不是崩溃
                self._enable = False
                print(f'[System][IOCard] 中断函数设置失败(ret={ret}), IO 卡功能降级为不可用')

    def registerCallback(self, callback: Callable):
        self._interrupt_callback_pool.append(callback)

    def setOutPutData(self,
                      ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                      ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None,
                      ch8: int = None, ch9: int = None, ch10: int = None, ch11: int = None,
                      ch12: int = None, ch13: int = None, ch14: int = None, ch15: int = None
                      ):
        if not self._enable: return -1
        chs = (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15)
        chs = [c1 if c2 is None else c2 for c1, c2 in zip(self._output_chs, chs)]
        self._output_chs = chs
        # 硬件只有 8 路输出, ch8~ch15 仅保存在内存中
        string = self.to8bit(*chs[:8], revise=True)
        ret = lib.WY_SetOutPutData(self._number, string)
        if ret != 0:
            print(f'[System][IOCard] 写输出失败(ret={ret})')
        return ret

    def getInputData(self):
        """ 读取 8 路输入. 失败时返回空列表(不抛异常, 供中断回调使用) """
        if not self._enable:
            return []
        try:
            data = ctypes.c_ubyte()  # 分配 1 字节
            ret = lib.WY_GetInPutData(self._number, ctypes.byref(data))
            if ret != 0:
                print(f'[System][IOCard] 读输入失败(ret={ret})')
                return []
            mask = data.value
            return [(mask >> i) & 1 for i in range(8)]
        except Exception as e:
            print(f'[System][IOCard] 读输入异常: {e}')
            return []

    def setRiseInterrupEnbale(self,
                              ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                              ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None,
                              ch8: int = None, ch9: int = None, ch10: int = None, ch11: int = None,
                              ch12: int = None, ch13: int = None, ch14: int = None, ch15: int = None
                              ):
        if not self._enable: return -1
        chs = (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15)
        enable = [c1 if c2 is None else c2 for c1, c2 in zip(self._rise_interrupt_enable, chs)]
        self._rise_interrupt_enable = enable
        ret = lib.WY_SetInterruptPortEnable(self._number,
                                            self.to16bit(*self._rise_interrupt_enable, revise=False),
                                            self.to16bit(*self._fall_interrupt_enable, revise=False), )
        if ret != 0:
            print(f'[System][IOCard] 设置上升沿中断使能失败(ret={ret})')
        return ret

    def setFallInterrupEnbale(self,
                              ch0: int = None, ch1: int = None, ch2: int = None, ch3: int = None,
                              ch4: int = None, ch5: int = None, ch6: int = None, ch7: int = None,
                              ch8: int = None, ch9: int = None, ch10: int = None, ch11: int = None,
                              ch12: int = None, ch13: int = None, ch14: int = None, ch15: int = None
                              ):
        if not self._enable: return -1
        chs = (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15)
        enable = [c1 if c2 is None else c2 for c1, c2 in zip(self._fall_interrupt_enable,chs)]
        self._fall_interrupt_enable = enable
        ret = lib.WY_SetInterruptPortEnable(self._number,
                                            self.to16bit(*self._rise_interrupt_enable, revise=False),
                                            self.to16bit(*self._fall_interrupt_enable, revise=False), )
        if ret != 0:
            print(f'[System][IOCard] 设置下降沿中断使能失败(ret={ret})')
        return ret


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
