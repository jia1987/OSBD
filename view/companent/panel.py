from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPaintEvent, QPainter, QPen
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from .button import ToolButton
from .icon import Icon
from .label import Label
from ..common import Theme


class PanelButton(QWidget):
    """导航栏"""

    clicked = pyqtSignal()

    def __init__(self, text: str, icon: Union[str, Icon], parent: QWidget = None):
        super(PanelButton, self).__init__(parent=parent)

        self._btn = ToolButton(self)
        self._btn.setIcon(icon)
        self._btn.setFixedSize(48, 48)
        self._label = Label(text=text, fontSize=16, parent=self)

        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addWidget(self._btn, alignment=Qt.AlignCenter)
        self.viewLayout.addWidget(self._label, alignment=Qt.AlignCenter)
        self.viewLayout.setSpacing(5)

        self._btn.clicked.connect(self.clicked.emit)


class Panel(QWidget):
    def __init__(self, parent):
        self._now_btn: PanelButton = None
        super(Panel, self).__init__(parent)
        self.btns = []

        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(10, 0, 0, 0)
        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.viewLayout.setSpacing(18)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        # self.setFixedSize(164, 1164)

    def addButton(self, text: str, icon: Union[str, Icon], onClicked=None):
        btn = PanelButton(text=text, icon=icon)
        # btn.show()
        self.btns.append(btn)
        self.viewLayout.insertWidget(self.viewLayout.count() - 1, btn)
        if onClicked is not None:
            btn.clicked.connect(onClicked)
        btn.clicked.connect(self._onBtnClicked)
        return btn

    def _onBtnClicked(self):
        btn: PanelButton = self.sender()
        self._now_btn = btn
        self.window().update()

    def paintEvent(self, e: QPaintEvent) -> None:
        if self._now_btn is not None:
            geometry = self._now_btn.geometry()
            painter = QPainter(self)
            pen = QPen(QPen(Theme.GrayColor, 2))
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(geometry.topLeft() + QPoint(-3, 0), geometry.bottomLeft() + QPoint(-3, 0))
        super(Panel, self).paintEvent(e)
