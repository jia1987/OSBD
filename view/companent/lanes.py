""" 缺陷分布泳道总览: 左/上/右/下/放电 五条 FaultLine + 刻度标签
复用 FaultLine(带缓存与降采样), 放电道橙色刻度; 滚动窗口由调用方 setScope 控制 """
from PyQt5.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QColor

from .fault_overview import FaultLine
from .label import Label
from ..common import Theme


class LanesOverview(QWidget):
    LANE_LABELS = ['左', '上', '右', '下', '放电']

    def __init__(self, parent=None):
        super(LanesOverview, self).__init__(parent)
        self.lines = []
        self._scale_labels = []
        self._grid = QGridLayout()
        self._grid.setSpacing(4)
        for i, lab in enumerate(self.LANE_LABELS):
            line = FaultLine(self, tick_color=QColor(Theme.ORANGE if lab == '放电' else Theme.RED))
            self.lines.append(line)
            label = Label(text=lab, fontSize=11)
            label.setStyleSheet(
                f'color:{Theme.ORANGE if lab == "放电" else Theme.TXT2};background:transparent;')
            self._grid.addWidget(label, i, 0)
            self._grid.addWidget(line, i, 1)
        self._grid.setColumnStretch(1, 1)
        # 底部刻度
        self._scale_layout = QHBoxLayout()
        self._scale_layout.setSpacing(0)
        for i in range(5):
            sl = Label(text='', fontSize=10)
            sl.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
            self._scale_labels.append(sl)
            self._scale_layout.addWidget(sl, 1)
        self._grid.addLayout(self._scale_layout, 5, 1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 6, 8, 4)
        outer.addLayout(self._grid)

    def addPoint(self, lane: int, distance: float):
        if 0 <= lane < len(self.lines):
            self.lines[lane].addPoint(distance)

    def addPoints(self, lane: int, distances):
        for d in distances:
            self.addPoint(lane, d)

    def setScope(self, minimum: float, maximum: float):
        if minimum == maximum:
            maximum = minimum + 1
        span = maximum - minimum
        for i, sl in enumerate(self._scale_labels):
            sl.setText(f'{minimum + span * i / (len(self._scale_labels) - 1):.2f}m')
        for line in self.lines:
            line.setScope(minimum, maximum)
            line.update()

    def clear(self):
        for line in self.lines:
            line.clear()
