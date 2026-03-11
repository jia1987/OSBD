from ...companent import Pivot, LightnInterface
from core.signal_bus import SignalBus
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QOpenGLShader, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRectF
from ...companent import FaultOverview
from core.pipeline import faultDetectionPipeline
from core.signal_bus import SignalBus
from typing import List, Set

class LightnInterface(LightnInterface):
    """实时更新最新的放电检测结果数据"""
    def __init__(self, parent=None):
        super(LightnInterface,self).__init__(parent=parent)

        # 当批次更新后, 重新计数
        SignalBus.batchUpdated.connect(self.clear)
        SignalBus.faultUpdated.connect(self.onFaultUpdated)
        self.update()

    def onFaultUpdated(self):
        output = faultDetectionPipeline.lightningOutput()
        if output.fault:
            self.setDistance(output.distance)
            self.update()