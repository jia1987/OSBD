""" 状态芯片: 圆角胶囊 + 状态点 + 文案 (底部状态栏/标题栏/设置页状态) """
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import QWidget

from .font import getFont
from ..common import Theme

_STATE_COLORS = {
    'ok': Theme.GREEN,     # 已连接/已启用
    'err': Theme.RED,      # 已断开/故障
    'off': '#5A6274',      # 未启用
    'warn': Theme.YELLOW,  # 警告/待处理
    'accent': Theme.ACCENT,
}


class StatusChip(QWidget):
    def __init__(self, text: str = '', state: str = 'ok', parent=None):
        super(StatusChip, self).__init__(parent)
        self._text = text
        self._state = state
        self._font = getFont(12)
        self.setFixedHeight(26)
        self._update_width()

    def setText(self, text: str):
        self._text = text
        self._update_width()
        self.update()

    def setState(self, state: str):
        if state != self._state:
            self._state = state
            self.update()

    def state(self):
        return self._state

    def _update_width(self):
        from PyQt5.QtGui import QFontMetrics
        w = QFontMetrics(self._font).horizontalAdvance(self._text) + 36
        self.setFixedWidth(max(w, 60))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        h = self.height()
        # 胶囊底
        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.setBrush(QColor('#262B38'))
        painter.drawRoundedRect(0, 0, self.width() - 1, h - 1, h / 2, h / 2)
        # 状态点
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(_STATE_COLORS.get(self._state, '#5A6274')))
        painter.drawEllipse(10, h // 2 - 5, 10, 10)
        # 文案
        painter.setPen(QColor(Theme.TXT))
        painter.setFont(self._font)
        painter.drawText(26, 0, self.width() - 32, h, Qt.AlignVCenter | Qt.AlignLeft, self._text)
