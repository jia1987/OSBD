from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QOpenGLShader, QPainter, QPen
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRectF
from .label import Label
from .edge import EdgegWidget
from core.pipeline import faultDetectionPipeline
from typing import List, Set


class FaultLine(QWidget):
    """ 显示一根漆包线其中一个面上的缺陷所在点 """

    def __init__(self, parent=None):
        super(FaultLine, self).__init__(parent)
        # 纯在缺陷的点
        self.fualt_point: Set[float] = set()
        self._scope = (0, 1)
        self.clear()

    def setScope(self, minimum, maximum):
        """ 设置范围 """
        self._scope = (minimum, maximum)

    def addPoint(self, point: float):
        """ 添加一个缺陷点"""
        self.fualt_point.add(point)

    def clear(self):
        self.fualt_point.clear()
        self._scope = (0, 1)

    def paintEvent(self, event):
        super(FaultLine, self).paintEvent(event)
        rect = self.rect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.gray)
        pen.setWidth(self.height() // 8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(self.height() // 8, rect.height() // 2, rect.width() - self.height() // 8, rect.height() // 2)

        # =======================
        # 绘制缺陷点
        # =======================
        if len(self.fualt_point) > 0:
            rect = QRectF(0, self.height() * (1 / 2 - 1 / 4), 2, rect.height() / 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.red)
            _min, _max = self._scope
            _scope = _max - _min
            for point in self.fualt_point:
                # 使用两个像素表示缺陷
                point = (point - _min) / _scope * self.width()
                rect.moveTo(point, rect.top())
                painter.drawRoundedRect(rect, 1, 1)


class FaultOverview(EdgegWidget):
    """ 显示一根漆包线上缺陷的所在点 """

    def __init__(self, parent=None):
        super(FaultOverview, self).__init__(parent)
        self.left_line = FaultLine(self)
        self.top_line = FaultLine(self)
        self.right_line = FaultLine(self)
        self.bottom_line = FaultLine(self)
        self.lightn_line = FaultLine(self)
        self.minimumLabel = Label(parent=self, fontSize=12)
        self.maximumLabel = Label(parent=self, fontSize=12)

        self.viewLayout = QVBoxLayout(self)
        self.hlayout = QHBoxLayout()
        self.gridLayout = QGridLayout()
        add_a_line = lambda i, w, text: (self.gridLayout.addWidget(w, i, 1),
                                         self.gridLayout.addWidget(Label(text=text), i, 0))

        add_a_line(i=0, w=self.left_line, text='左')
        add_a_line(i=1, w=self.top_line, text='上')
        add_a_line(i=2, w=self.right_line, text='右')
        add_a_line(i=3, w=self.bottom_line, text='下')
        add_a_line(i=4, w=self.lightn_line, text='放电')
        self.gridLayout.setColumnStretch(1, 1)
        self.hlayout.addWidget(self.minimumLabel)
        self.hlayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.hlayout.addWidget(self.maximumLabel)
        self.viewLayout.addLayout(self.gridLayout)
        self.gridLayout.addLayout(self.hlayout, 5, 1)

    def setScope(self, minimum, maximum):
        if minimum == maximum:
            maximum = minimum + 1
        self.minimumLabel.setText(f"{minimum:.2f}")
        self.maximumLabel.setText(f"{maximum:.2f}")
        self.left_line.setScope(minimum, maximum)
        self.top_line.setScope(minimum, maximum)
        self.right_line.setScope(minimum, maximum)
        self.bottom_line.setScope(minimum, maximum)
        self.lightn_line.setScope(minimum, maximum)
        self.left_line.update()
        self.top_line.update()
        self.right_line.update()
        self.bottom_line.update()
        self.lightn_line.update()

    def clear(self):
        self.left_line.clear()
        self.top_line.clear()
        self.right_line.clear()
        self.bottom_line.clear()
        self.lightn_line.clear()

    def scope(self):
        return self.left_line._scope
