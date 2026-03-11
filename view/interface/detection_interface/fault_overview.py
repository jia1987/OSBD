from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QOpenGLShader, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRectF
from ...companent import FaultOverview
from core.pipeline import faultDetectionPipeline
from core.signal_bus import SignalBus
from typing import List, Set


class OnlineFaultOverview(FaultOverview):
    """ 实时更新最新的检测结果数据 """
    def __init__(self, parent=None):
        super(OnlineFaultOverview, self).__init__(parent)
        # 当批次更新后, 重新计数
        SignalBus.batchUpdated.connect(self.clear)
        SignalBus.faultUpdated.connect(self.onFaultUpdated)

    def onFaultUpdated(self):
        """ 缺陷更新 """
        distance = faultDetectionPipeline.accumulatedDistance(obj='batch')
        minimum, maximum = self.scope()
        for line, ctx in zip((self.left_line, self.top_line, self.right_line, self.bottom_line),
                             faultDetectionPipeline.CHANNELS):
            camera = faultDetectionPipeline.channels(ctx=ctx)
            # 如果没有进行检测可以跳过
            if camera.camera is None: continue
            if camera.faults is None: continue
            if len(camera.faults) == 0: continue

            minimum = min(minimum, distance)
            maximum = max(maximum, distance)
            line.addPoint(distance)
            line.update()
        # =============
        # 放电
        # ============
        if faultDetectionPipeline.lightningOutput().fault == True:
            minimum = min(minimum, distance)
            maximum = max(maximum, distance)
            self.lightn_line.addPoint(distance)
            self.update()
        self.setScope(minimum=minimum, maximum=maximum)
