import threading
import time

from .device import IOCard
from .device import LightningOutput
from ..config import config


class LightningMixin():
    """ 放电检测 """

    def __init__(self):
        # io card
        self.__io_card = IOCard.getCard(number=0)
        self.__io_card.registerCallback(self._interrupt)
        self.__io_card.setFallInterrupEnbale(ch0=1)
        # 是否使能
        self._is_lightning_enabled = False
        # 结果缓存 (供界面显示)
        self._output = None
        # 事件锁与待处理事件标记
        # 中断线程只置位, 由检测线程原子地取走, 避免去抖窗口内事件被丢弃
        self._lightning_lock = threading.Lock()
        self._pending_event = False
        # 最近一次缺陷的距离 (供界面显示)
        self._last_distance = 0.0
        # 界面显示用的缺陷有效截止时间
        self._active_until = 0.0

    def setLightningEnabled(self, enabled: bool) -> None:
        if enabled:
            baudrate = int(config.get(config.Lightning_Baudrate))
            port = str(config.get(config.Lightning_Port))
            # print(f"[System] Connect Lightning(Baudrate:{baudrate}, Port:{port})...")
            print(f"[System] Connect Lightning...")
        else:
            print(f"[System] Disconnect Lightning...")
        self._is_lightning_enabled = enabled
        if not enabled:
            with self._lightning_lock:
                self._pending_event = False
                self._output = None

    def _interrupt(self):
        """ 中断函数 (运行于 C 回调线程, 不允许抛出异常) """
        try:
            if not self._is_lightning_enabled: return
            data = self.__io_card.getInputData()
            if data and data[0] == 1:
                with self._lightning_lock:
                    self._pending_event = True
                    self._output = LightningOutput(fault=True)
        except Exception as e:
            print(f'[System][Lightning] 中断处理异常: {e}')

    def takeLightningEvent(self) -> bool:
        """ 原子地取走一次放电事件 (取走后不删除显示缓存) """
        with self._lightning_lock:
            v = self._pending_event
            self._pending_event = False
            return v

    def markLightningReported(self, distance: float, active: float = 0.3):
        """ 记录一次已上报的放电缺陷, 供界面短暂显示 """
        with self._lightning_lock:
            self._last_distance = distance
            self._active_until = time.time() + active
            if self._output is not None:
                self._output.distance = distance

    def lightningOutput(self) -> LightningOutput:
        """ 读取一次结果 """
        if not self._is_lightning_enabled:
            return LightningOutput()
        with self._lightning_lock:
            if self._active_until > time.time():
                return LightningOutput(fault=True, distance=self._last_distance)
            return LightningOutput()

    def clearLightningOutput(self):
        """ 清空 """
        with self._lightning_lock:
            self._output = None
            self._pending_event = False
            self._active_until = 0.0

    def isLightningEnabled(self):
        """ 放电检测使能 """
        return self._is_lightning_enabled
