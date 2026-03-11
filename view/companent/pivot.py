from PyQt5.QtWidgets import QSpacerItem, QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QSizePolicy
from PyQt5.QtWidgets import QToolButton, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from .icon import Icon
from .label import Label
from typing import Union, Optional
from .button import PushButton




class Pivot(QWidget):
    def __init__(self, parent):
        super(Pivot, self).__init__(parent)
        self.btns = []

        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.viewLayout.setSpacing(18)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        # self.setFixedSize(164, 1164)

    def addButton(self, text: str, icon: Union[str, Icon] = None, onClicked=None):
        btn = PushButton(text=text)
        # btn.show()
        self.btns.append(btn)
        self.viewLayout.insertWidget(self.viewLayout.count() - 1, btn)
        if onClicked is not None:
            btn.clicked.connect(onClicked)
        return btn
