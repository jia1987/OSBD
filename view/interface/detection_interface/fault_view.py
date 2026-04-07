from functools import partial
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QStackedWidget, QWidget

from core import faultDetectionPipeline
from ...companent import Label, Pivot, EdgegWidget, PushButton
from ...companent import PipelineCameraLabel, PipelineResultLabel, MaskBox


class FaultView(QWidget):
    def __init__(self, parent=None):
        super(FaultView, self).__init__(parent)
        self.returnBtn = PushButton(parent=self, text=self.tr("返回"))
        self.mainLayout = QVBoxLayout(self)
        self.viewLayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        self.mainLayout.addLayout(self.viewLayout)
        self.mainLayout.addLayout(self.hlayout)
        self.mainLayout.setStretch(0, 1)
        self.mainLayout.setStretch(1, 0)
        self.hlayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.hlayout.addWidget(self.returnBtn)
        self.hlayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.hlayout.setStretch(0, 1)
        self.hlayout.setStretch(1, 1)
        self.hlayout.setStretch(2, 1)
        self.returnBtn.setFixedHeight(64)

        self.returnBtn.clicked.connect(self.close)

