from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel

from .font import setFont


class Label(QLabel):
    def __init__(self, text: str='', fontSize: int = 18, weight=QFont.Normal, parent=None):
        super().__init__(text, parent)

        setFont(self, fontSize=fontSize, weight=weight)
