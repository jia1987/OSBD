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


class CameraDisplayInterface(EdgegWidget):

    def __init__(self, parent=None):
        super(CameraDisplayInterface, self).__init__(parent)

        self.initWidget()
        self.initConnect()
        self.initLayout()

    def initWidget(self):
        # 导航栏
        self.pivot = Pivot(self)
        self.pivot.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.resultDisplay = QWidget(self)
        self.origineDisplay = QWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self._result_labels: List[PipelineResultLabel] = []
        for idx in faultDetectionPipeline.CHANNELS:
            label = PipelineResultLabel(ctx=idx, parent=self)
            self._result_labels.append(label)

        self._merge_labels: List[PipelineCameraLabel] = []
        for idx in faultDetectionPipeline.CHANNELS:
            label = PipelineCameraLabel(ctx=idx, parent=self)
            self._merge_labels.append(label)

    def initConnect(self):
        for label in self._result_labels:
            label.clicked.connect(partial(self._onLabelClickedEvent, label))
        for label in self._merge_labels:
            label.clicked.connect(partial(self._onLabelClickedEvent, label))

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(5, 5, 5, 5)
        self.hlayout1 = QHBoxLayout()
        self.hlayout1.addWidget(self.pivot)
        self.hlayout1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.viewLayout.addLayout(self.hlayout1)
        self.viewLayout.addWidget(self.stackedWidget)
        self.viewLayout.setStretch(0, 0)
        self.viewLayout.setStretch(1, 1)

        self.viewLayout2 = QGridLayout(self.origineDisplay)
        self.viewLayout2.setContentsMargins(0, 0, 0, 0)
        self.viewLayout2.addWidget(Label(self.tr('原始图像'), parent=self, weight=QFont.Bold, fontSize=20), 0, 0)
        for idx, label in enumerate(self._merge_labels):
            self.viewLayout2.addWidget(Label(f"管线{idx + 1}"), 1, idx, alignment=Qt.AlignCenter)
            self.viewLayout2.addWidget(label, 2, idx)
        self.viewLayout2.setRowStretch(0, 0)
        self.viewLayout2.setRowStretch(1, 0)
        self.viewLayout2.setRowStretch(2, 1)

        self.viewLayout3 = QGridLayout(self.resultDisplay)
        self.viewLayout3.setContentsMargins(0, 0, 0, 0)
        self.viewLayout3.addWidget(Label(self.tr('检测结果'), parent=self, weight=QFont.Bold, fontSize=20), 0, 0)
        for idx, label in enumerate(self._result_labels):
            self.viewLayout3.addWidget(Label(f"管线{idx + 1}"), 1, idx, alignment=Qt.AlignCenter)
            self.viewLayout3.addWidget(label, 2, idx)
        self.viewLayout3.setRowStretch(0, 0)
        self.viewLayout3.setRowStretch(1, 0)
        self.viewLayout3.setRowStretch(2, 1)

        self.pivot.addButton(text=self.tr('检测结果'),
                             onClicked=lambda: self.stackedWidget.setCurrentWidget(self.origineDisplay))
        self.pivot.addButton(text=self.tr('检测结果'),
                             onClicked=lambda: self.stackedWidget.setCurrentWidget(self.resultDisplay))
        self.stackedWidget.addWidget(self.origineDisplay)
        self.stackedWidget.addWidget(self.resultDisplay)

    def _onLabelClickedEvent(self, label: PipelineCameraLabel):
        view = FaultView()
        label = type(label)(ctx=label.ctx())
        view.viewLayout.addWidget(label)

        # mask
        w = MaskBox(parent=self.window())
        w.setWidget(widget=view)
        w.exec()
