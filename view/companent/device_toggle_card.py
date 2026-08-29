""" 设备开关卡: 状态点 + 文案 + ToggleButton (实时检测页设备控制) """
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from .font import getFont
from .toggle_btn import ToggleButton
from ..common import Theme


class DeviceToggleCard(QWidget):
    def __init__(self, text: str = '', parent=None):
        super(DeviceToggleCard, self).__init__(parent)
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)
        self._label = QLabel(text)
        self._label.setFont(getFont(13, True))
        self._label.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        layout.addWidget(self._label, 1)
        self.toggle = ToggleButton(self)
        layout.addWidget(self.toggle)

    def setState(self, on: bool, text: str = None):
        """ 同步设备状态: 文案 + 开关位置 (setChecked 仅在变化时发信号, 安全) """
        if text is not None:
            self._label.setText(text)
        self.toggle.setChecked(on)
        self.update()

    def setEnabled_(self, on: bool):
        self.toggle.setChecked(on)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.setBrush(QColor(Theme.CARD2))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
        # 状态点
        on = self.toggle.isChecked()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(Theme.GREEN if on else '#5A6274'))
        painter.drawEllipse(12, self.height() // 2 - 5, 10, 10)
