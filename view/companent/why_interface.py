from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QSpacerItem, QLabel
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from .edge import EdgegWidget
from .label import Label


class LightnInterface(EdgegWidget):
    """ 放电检测的信息组件 """
    def __init__(self, parent=None):
        super(LightnInterface, self).__init__(parent)
        self.setMinimumSize(256, 64)

        self.distanceLabel = Label(text=self.tr('距离:'), parent=self)

        self.viewlayout = QVBoxLayout(self)
        self.viewlayout.setContentsMargins(5, 5, 5, 5)
        self.viewlayout.addWidget(Label(parent=self, text=self.tr('放电检测')))
        self.viewlayout.addWidget(self.distanceLabel, alignment=Qt.AlignLeft)
        self.viewlayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.clear()

    def setDistance(self, distance):
        self.distanceLabel.setText(f"距离:{distance:.2f}m")

    def clear(self):
        self.distanceLabel.setText("距离:")

    def load(self, path):
        pass
