import os.path
import json
from PyQt5.QtGui import QIcon, QPainter, QPen
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, QRect
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QSpacerItem
from PyQt5.QtWidgets import QComboBox, QInputDialog, QMessageBox, QPushButton, QLabel, QLineEdit, QSizePolicy

from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget


class EdgegWidget(QWidget):

    def paintEvent(self, event):
        super(EdgegWidget, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.gray, 2))

        painter.drawRoundedRect(QRect(2, 2, self.width() - 4, self.height() - 4), 8, 8)
