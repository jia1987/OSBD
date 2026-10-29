from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel

from .font import setFont


class Label(QLabel):
    def __init__(self, text: str='', fontSize: int = 18, weight=QFont.Normal, parent=None):
        super().__init__(text, parent)

        setFont(self, fontSize=fontSize, weight=weight)
        # 全局 QWidget 底色规则会在卡片上给标签画出深色块; 标签默认透明,
        # 调用方若再 setStyleSheet(带背景) 会排在后面覆盖之
        self.setStyleSheet('background-color:transparent;')

    def setStyleSheet(self, ss: str):
        if 'background' not in ss:
            ss = 'background-color:transparent;' + ss
        super().setStyleSheet(ss)
