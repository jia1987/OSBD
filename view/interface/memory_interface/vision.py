import os
from urllib.response import addinfo

from PyQt5.QtCore import QTimer, QStandardPaths, QStringListModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QListView, QGridLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QListView

from ...companent import Label, Pivot, LightnInterface, EdgegWidget, ResultLabel,ResultEditWidget,MaskBox
# from .image import ResultLabel
from core.const import Path
from core.pipeline import faultDetectionPipeline
from functools import partial

class VisionDetectWidgwt(EdgegWidget):
    """ 四个相机的检测结果展示"""

    def __init__(self, *args, **kwargs):
        super(VisionDetectWidgwt, self).__init__(*args, **kwargs)

        self.initWidget()
        self.initLayout()
        self.initConnect()

    def initWidget(self):
        self.result_label_1 = ResultLabel(parent=self)
        self.result_label_2 = ResultLabel(parent=self)
        self.result_label_3 = ResultLabel(parent=self)
        self.result_label_4 = ResultLabel(parent=self)

    def initConnect(self):
        self.result_label_1.clicked.connect(partial(self.onLabelCilicked,self.result_label_1))
        self.result_label_2.clicked.connect(partial(self.onLabelCilicked,self.result_label_2))
        self.result_label_3.clicked.connect(partial(self.onLabelCilicked,self.result_label_3))
        self.result_label_4.clicked.connect(partial(self.onLabelCilicked,self.result_label_4))

    def initLayout(self):
        self.viewLayout = QGridLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        for i, label in enumerate((self.result_label_1, self.result_label_2, self.result_label_3, self.result_label_4)):
            self.viewLayout.addWidget(Label(text=self.tr(f'通道{i + 1}'), fontSize=16, parent=self), 0, i,
                                      alignment=Qt.AlignCenter)
            self.viewLayout.addWidget(label, 1, i)
        self.viewLayout.setRowStretch(1, 1)

    def load(self, path: str):
        for label, camera_name in zip((self.result_label_1,
                                       self.result_label_2,
                                       self.result_label_3,
                                       self.result_label_4,),
                                      faultDetectionPipeline.CHANNELS):
            label.setResult(os.path.join(path, camera_name))

    def onLabelCilicked(self,label:ResultLabel):
        # mask
        w = MaskBox(parent=self.window())

        view = ResultEditWidget(parent=w)
        view.setResult(label.readPath())
        w.setWidget(widget=view)
        w.exec()