from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QOpenGLShader, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, QLineF
from .label import Label
from .edge import EdgegWidget
from ..common import Theme
from core.pipeline import faultDetectionPipeline
from typing import List, Set


class FaultLine(QWidget):
    """显示一根漆包线其中一个面上的缺陷所在点（优化版）"""

    def __init__(self, parent=None, tick_color: QColor = None):
        super(FaultLine, self).__init__(parent)
        self.fualt_point: Set[float] = set()
        self._scope = (0, 1)
        self._tick_color = tick_color or QColor(Theme.RED)

        # ====== 优化缓存 ======
        self._points_px = []  # 归一化后的点（0~1）
        self._cache_dirty = True
        self._pixmap_cache = None

        # 控制最大绘制点数（防止卡顿）
        self._max_points = 2000

        self.clear()

    def setScope(self, minimum, maximum):
        """设置范围"""
        self._scope = (minimum, maximum)
        self._cache_dirty = True
        self.update()

    def addPoint(self, point: float):
        """添加一个缺陷点"""
        self.fualt_point.add(point)
        self._cache_dirty = True

    def clear(self):
        self.fualt_point.clear()
        self._scope = (0, 1)
        self._points_px = []
        self._cache_dirty = True
        self.update()

    # =========================
    # 关键优化：预计算
    # =========================
    def _updateCache(self):
        if not self._cache_dirty:
            return

        _min, _max = self._scope
        _scope = _max - _min if _max != _min else 1.0

        # 归一化
        points = [(p - _min) / _scope for p in self.fualt_point]

        # 过滤非法值
        points = [p for p in points if 0 <= p <= 1]

        # ===== 降采样（关键优化）=====
        if len(points) > self._max_points:
            step = len(points) // self._max_points
            points = points[::step]

        self._points_px = points
        self._cache_dirty = False

    # =========================
    # 可选：Pixmap缓存（极大提升）
    # =========================
    def _updatePixmapCache(self):
        if self._pixmap_cache is not None and not self._cache_dirty:
            return

        self._updateCache()

        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 画线(深色主题基线)
        g = h // 8
        pen = QPen(QColor(Theme.BORDER))
        pen.setWidth(g)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(g, g * 4, w - g, g * 4)

        # 画点（批量）

        if self._points_px:
            # QPen(brush: Union[QBrush, QColor, Qt.GlobalColor, QGradient],
            # width: float,
            # style: Qt.PenStyle = Qt.SolidLine,
            # cap: Qt.PenCapStyle = Qt.SquareCap,
            # join: Qt.PenJoinStyle = Qt.BevelJoin
            painter.setPen(QPen(self._tick_color, 2, Qt.SolidLine, Qt.RoundCap))
            y = h / 4
            w = w - g * 2
            lines = [QLineF(g + px * w, y,
                            g + px * w, y * 3) for px in self._points_px]

            painter.drawLines(lines)

        painter.end()
        self._pixmap_cache = pixmap

    def resizeEvent(self, event):
        super(FaultLine, self).resizeEvent(event)
        self._cache_dirty = True

    # =========================
    # 绘制
    # =========================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 使用缓存
        self._updatePixmapCache()

        if self._pixmap_cache:
            painter.drawPixmap(0, 0, self._pixmap_cache)


class FaultOverview(EdgegWidget):
    """ 显示一根漆包线上缺陷的所在点 """

    def __init__(self, parent=None):
        super(FaultOverview, self).__init__(parent)
        self.left_line = FaultLine(self)
        self.top_line = FaultLine(self)
        self.right_line = FaultLine(self)
        self.bottom_line = FaultLine(self)
        self.lightn_line = FaultLine(self, tick_color=QColor(Theme.ORANGE))
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
