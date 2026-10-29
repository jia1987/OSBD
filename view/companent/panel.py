from typing import Union

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QColor, QFont
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from .font import getFont
from .icon import Icon, drawIcon
from .label import Label
from ..common import Theme


class PanelButton(QWidget):
    """导航栏按钮 (设计稿 P2): 图标 + 文字 横排, 选中态 = 卡片底色 + 主色图标"""

    clicked = pyqtSignal()

    def __init__(self, text: str, icon: Union[str, Icon], parent: QWidget = None):
        super(PanelButton, self).__init__(parent=parent)

        self._icon = icon
        self._text = text
        self._checked = False
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = checked
            self.update()

    def isChecked(self) -> bool:
        return self._checked

    def mouseReleaseEvent(self, e):
        if self.rect().contains(e.pos()):
            self.clicked.emit()
        super(PanelButton, self).mouseReleaseEvent(e)

    def paintEvent(self, e: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 选中底色
        if self._checked:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(Theme.CARD2))
            painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
        # 图标 (svg 换色: 选中=主色 未选中=次级文字色)
        color = Theme.ACCENT if self._checked else Theme.TXT2
        drawIcon(self._icon, painter, QRectF(14, (self.height() - 20) / 2, 20, 20), fill=color)
        # 文字
        painter.setPen(QColor(Theme.TXT if self._checked else Theme.TXT2))
        painter.setFont(getFont(14, QFont.Bold if self._checked else QFont.Normal))
        painter.drawText(46, 0, self.width() - 52, self.height(),
                         Qt.AlignVCenter | Qt.AlignLeft, self._text)


class Panel(QWidget):
    def __init__(self, parent):
        self._now_btn: PanelButton = None
        super(Panel, self).__init__(parent)
        self.btns = []
        self.setFixedWidth(188)

        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(10, 12, 10, 0)
        self.viewLayout.setSpacing(6)

    def addButton(self, text: str, icon: Union[str, Icon], onClicked=None):
        btn = PanelButton(text=text, icon=icon, parent=self)
        self.btns.append(btn)
        self.viewLayout.addWidget(btn)
        if self._now_btn is None:
            self._now_btn = btn
            btn.setChecked(True)
        if onClicked is not None:
            btn.clicked.connect(onClicked)
        btn.clicked.connect(self._onBtnClicked)
        return btn

    def addFooter(self, text: str):
        """ 底部版本/授权信息 (设计稿 P2 左下角) """
        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        lab = Label(text=text, fontSize=10)
        lab.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        self.viewLayout.addWidget(lab)

    def _onBtnClicked(self):
        btn: PanelButton = self.sender()
        if self._now_btn is btn:
            return
        if self._now_btn is not None:
            self._now_btn.setChecked(False)
        self._now_btn = btn
        btn.setChecked(True)
        self.update()

    def paintEvent(self, e: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 导航栏底色
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(Theme.BAR))
        painter.drawRect(0, 0, self.width(), self.height())
        # 选中项左侧主色竖条
        if self._now_btn is not None:
            geometry = self._now_btn.geometry()
            pen = QPen(QColor(Theme.ACCENT), 3)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawLine(geometry.topLeft(), geometry.bottomLeft())
        super(Panel, self).paintEvent(e)
