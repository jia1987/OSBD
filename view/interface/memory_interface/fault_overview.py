import os

from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QPixmap, QOpenGLShader, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRectF

from ...companent import FaultOverview
from core.pipeline import faultDetectionPipeline
from typing import List, Set


class BatchFaultOverview(FaultOverview):
    """ 读取本地数据, 展示在一条漆包线上的权限位置"""

    def __init__(self, parent=None):
        super(BatchFaultOverview, self).__init__(parent)

    def load(self, path):
        self.clear()
        minimum, maximum = None, None
        print("go")
        for i in os.listdir(path):
            _f = tuple(os.listdir(os.path.join(path, i)))
            i = float(i)
            minimum = min(minimum, i) if minimum is not None else i
            maximum = max(maximum, i) if maximum is not None else i
            print(i)
            if 'c1' in _f:
                self.left_line.addPoint(i)
            if 'c2' in _f:
                self.top_line.addPoint(i)
            if 'c3' in _f:
                self.right_line.addPoint(i)
            if 'c4' in _f:
                self.bottom_line.addPoint(i)
            if 'lightning' in _f:
                self.lightn_line.addPoint(i)
        self.setScope(minimum=minimum, maximum=maximum)
        self.update()
