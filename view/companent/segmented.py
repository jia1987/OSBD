""" 分段选择控件 (原始图/结果图、通道切换等) """
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from .font import getFont
from ..common import Theme


class SegmentedControl(QWidget):
    indexChanged = pyqtSignal(int)

    def __init__(self, items, parent=None, active: int = 0, item_width: int = 76, height: int = 26):
        super(SegmentedControl, self).__init__(parent)
        self._items = list(items)
        self._active = active
        self._item_w = item_width
        self.setFixedSize(item_width * len(self._items), height)
        self._font = getFont(12)

    def currentIndex(self) -> int:
        return self._active

    def setCurrentIndex(self, idx: int, emit: bool = False):
        if 0 <= idx < len(self._items) and idx != self._active:
            self._active = idx
            self.update()
            if emit:
                self.indexChanged.emit(idx)

    def mousePressEvent(self, event):
        idx = min(len(self._items) - 1, max(0, event.x() // self._item_w))
        if idx != self._active:
            self._active = idx
            self.update()
            self.indexChanged.emit(idx)
        super(SegmentedControl, self).mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        h = self.height()
        # 底
        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.setBrush(QColor(Theme.BAR))
        painter.drawRoundedRect(0, 0, self.width() - 1, h - 1, h / 2, h / 2)
        painter.setFont(self._font)
        for i, text in enumerate(self._items):
            x = i * self._item_w
            if i == self._active:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(Theme.ACCENT))
                painter.drawRoundedRect(x + 2, 2, self._item_w - 4, h - 4, (h - 4) / 2, (h - 4) / 2)
                painter.setPen(QColor('#FFFFFF'))
                f = self._font
                f.setBold(True)
                painter.setFont(f)
            else:
                painter.setPen(QColor(Theme.TXT2))
                f = self._font
                f.setBold(False)
                painter.setFont(f)
            painter.drawText(x, 0, self._item_w, h, Qt.AlignCenter, text)
