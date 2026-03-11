from core.pipeline import faultDetectionPipeline
from core.signal_bus import SignalBus


class Function():
    @staticmethod
    def swapBatch(batchName: str, wokerName: str = ''):
        """
        更换批次
        param> batchName:批次名
        """
        faultDetectionPipeline.swapBatch(batchName, wokerName)
        SignalBus.batchUpdated.emit(batchName, wokerName)

    @staticmethod
    def onFaultUpdated():
        """ 缺陷更新 """
        SignalBus.faultUpdated.emit()


faultDetectionPipeline.setCallback(callback=Function.onFaultUpdated)
