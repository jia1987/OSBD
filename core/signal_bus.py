from PyQt5.QtCore import QObject, pyqtSignal


class __SignalBus__(QObject):
    # 批次更新
    batchUpdated = pyqtSignal(str,str)
    # 缺陷更新
    faultUpdated = pyqtSignal()


SignalBus = __SignalBus__()
