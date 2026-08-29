import os.path
import json
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, QRect

from ..common import Theme
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QSpacerItem
from PyQt5.QtWidgets import QComboBox, QInputDialog, QMessageBox, QPushButton, QLabel, QLineEdit, QSizePolicy

from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget


class EdgegWidget(QWidget):
    """ 深色主题卡片容器: CARD 底色 + BORDER 圆角边框 """

    def paintEvent(self, event):
        super(EdgegWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRect(2, 2, self.width() - 4, self.height() - 4)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(Theme.CARD))
        painter.drawRoundedRect(rect, 8, 8)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(Theme.BORDER), 2))

        painter.drawRoundedRect(rect, 8, 8)
