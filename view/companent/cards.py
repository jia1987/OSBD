""" 设计稿卡片组件: Card(带标题容器) / StatCard(大数值) / KpiCard(值+单位+标签) """
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

from .font import getFont
from ..common import Theme


class Card(QWidget):
    """ 圆角卡片容器, 可选标题行 """

    def __init__(self, title: str = '', parent=None):
        super(Card, self).__init__(parent)
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(12, 10, 12, 12)
        self._outer.setSpacing(8)
        self._title = None
        self._header_extra = QHBoxLayout()
        if title:
            self._title = QLabel(title)
            self._title.setFont(getFont(14, True))
            self._title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
            self._outer.addWidget(self._title)
            self._outer.addLayout(self._header_extra)
        self._content = QVBoxLayout()
        self._content.setSpacing(8)
        self._outer.addLayout(self._content)

    def contentLayout(self) -> QVBoxLayout:
        return self._content

    def headerExtraLayout(self) -> QHBoxLayout:
        """ 标题右侧的附加布局(放按钮等) """
        return self._header_extra

    def setTitle(self, title: str):
        if self._title is None:
            self._title = QLabel(title)
            self._title.setFont(getFont(14, True))
            self._title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
            self._outer.insertWidget(0, self._title)
        else:
            self._title.setText(title)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(Theme.CARD))
        from PyQt5.QtGui import QPen
        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)


class StatCard(QWidget):
    """ 实时统计卡: 大数值 + 标签 """

    def __init__(self, num: str = '0', label: str = '', color: str = Theme.ACCENT, parent=None):
        super(StatCard, self).__init__(parent)
        self.setFixedHeight(72)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(2)
        self._num = QLabel(num)
        self._num.setFont(getFont(22, True))
        self._num.setAlignment(Qt.AlignCenter)
        self._num.setStyleSheet(f'color:{color};background:transparent;')
        self._label = QLabel(label)
        self._label.setFont(getFont(11))
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        layout.addWidget(self._num)
        layout.addWidget(self._label)

    def setNum(self, num, color: str = None):
        self._num.setText(str(num))
        if color:
            self._num.setStyleSheet(f'color:{color};background:transparent;')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        from PyQt5.QtGui import QPen
        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.setBrush(QColor(Theme.CARD2))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 6, 6)


class KpiCard(QWidget):
    """ 顶部 KPI 卡: 值 + 单位 + 小标签 """

    def __init__(self, label: str = '', value: str = '--', unit: str = '',
                 color: str = Theme.ACCENT, parent=None):
        super(KpiCard, self).__init__(parent)
        self.setFixedHeight(58)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        top = QHBoxLayout()
        top.setSpacing(4)
        self._value = QLabel(value)
        self._value.setFont(getFont(20, True))
        self._value.setStyleSheet(f'color:{color};background:transparent;')
        self._unit = QLabel(unit)
        self._unit.setFont(getFont(10))
        self._unit.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        self._unit.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        top.addWidget(self._value)
        top.addWidget(self._unit)
        top.addStretch(1)
        self._label = QLabel(label)
        self._label.setFont(getFont(11))
        self._label.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        layout.addLayout(top)
        layout.addWidget(self._label)

    def setValue(self, value: str, color: str = None):
        self._value.setText(str(value))
        if color:
            self._value.setStyleSheet(f'color:{color};background:transparent;')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        from PyQt5.QtGui import QPen
        painter.setPen(QPen(QColor(Theme.BORDER), 1))
        painter.setBrush(QColor(Theme.CARD))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 8, 8)
