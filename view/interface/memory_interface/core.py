import os
from urllib.response import addinfo

from PyQt5.QtCore import QTimer, QStandardPaths, QStringListModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QListView, QGridLayout
from PyQt5.QtWidgets import QApplication, QMainWindow, QListView

from ...companent import Label, Pivot, FaultOverview
from .image import ResultLabel
from .vision import VisionDetectWidgwt
from .navigation import Navigation
from .fault_overview import BatchFaultOverview
from core.const import Path
from core.database import UserManager
from core.pipeline import faultDetectionPipeline
from .lightning import  LightnReviewInterface

class MemoryhInterface(QWidget):
    """先前的缺陷检测结果的展示窗口"""
    def __init__(self, parent=None):
        self._check_batch_name = None
        self._manager = UserManager()
        super().__init__(parent)

        self.initWidget()
        self.initLayout()
        self.initConnect()

    def initWidget(self):
        self.navigation = Navigation(self)
        self.visionDetectWidgwt = VisionDetectWidgwt(self)
        self.lightnInterface = LightnReviewInterface(self)
        self.faultOverview = BatchFaultOverview(self)

    def initLayout(self):
        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout1 = QHBoxLayout()
        self.vLayout1 = QVBoxLayout()

        self.viewLayout.addWidget(self.navigation)
        self.hLayout1.addWidget(self.faultOverview)
        self.hLayout1.addWidget(self.lightnInterface)
        self.vLayout1.addLayout(self.hLayout1)
        self.vLayout1.addWidget(self.visionDetectWidgwt)
        self.viewLayout.addLayout(self.vLayout1)
        self.viewLayout.setStretch(0, 2)
        self.viewLayout.setStretch(1, 8)
        self.vLayout1.setStretch(0, 1)
        self.vLayout1.setStretch(1, 3)

    def initConnect(self):
        self.navigation.faultSetUpdated.connect(self._read_a_batch)
        self.navigation.faultLoadRequsted.connect(self._read_a_detect_point)

    def _read_a_batch(self, path):
        """ 点击 """
        print(13123123)
        batchName = os.path.basename(path)
        self.faultOverview.load(path=path)




    def _read_a_detect_point(self, path):
        """ 点击 """
        self.visionDetectWidgwt.load(path=path)
        self.lightnInterface.load(path=path)
