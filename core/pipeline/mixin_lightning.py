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
        # 结果缓存
        self._output = None

    def setLightningEnabled(self, enabled: bool) -> None:
        if enabled:
            baudrate = int(config.get(config.Lightning_Baudrate))
            port = str(config.get(config.Lightning_Port))
            # print(f"[System] Connect Lightning(Baudrate:{baudrate}, Port:{port})...")
            print(f"[System] Connect Lightning...")
        else:
            print(f"[System] Disconnect Lightning...")
        self._is_lightning_enabled = enabled

    def _interrupt(self):
        """ 中断函数 """
        if not self._is_lightning_enabled: return
        if self.__io_card.getInputData()[0] == 1:
            self._output = LightningOutput(fault=True)

    def lightningOutput(self) -> LightningOutput:
        """ 读取一次结果 """
        if not self._is_lightning_enabled:
            return LightningOutput()
        return self._output or LightningOutput()

    def clearLightningOutput(self):
        """ 清空 """
        self._output = None
    def isLightningEnabled(self):
        """ 放电检测使能 """
        return self._is_lightning_enabled
