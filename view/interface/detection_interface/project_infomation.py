import os.path


from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QTimer,Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QLineEdit, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QTableView, QHeaderView
from core.signal_bus import SignalBus
from view.companent import PipelineCameraLabel, PipelineResultLabel, Label,ResultLabel
from typing import List
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QVBoxLayout, QStackedWidget, QFrame, QWidget
from core import faultDetectionPipeline
from core.const import Path
from ...companent import Label, EdgegWidget,TableView,MaskBox
from .fault_view import FaultView

class BatchInfomationWidget(EdgegWidget):
    def __init__(self, parent):
        super(BatchInfomationWidget, self).__init__(parent)
        self.initWidget()
        self.initConnect()
        self.initLayout()

    def initWidget(self):
        self.batch_name_label = Label(text='检查结果:', fontSize=16, parent=self)
        self.table_view = TableView(self)
        self.table_view.setFrameShape(QFrame.NoFrame)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.verticalHeader().setHidden(True)
        # the model of table view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['位置', '传感器', '缺陷类型'])
        self.table_view.setModel(self.model)

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(5, 5, 5, 5)

        self.viewLayout.addWidget(self.batch_name_label)
        self.viewLayout.addWidget(self.table_view)
        self.viewLayout.setStretch(1, 1)

    def initConnect(self):
        SignalBus.batchUpdated.connect(
            lambda: self.batch_name_label.setText(self.tr('检查结果:') + faultDetectionPipeline.batchName()))
        SignalBus.batchUpdated.connect(lambda :self.model.clear())
        SignalBus.faultUpdated.connect(self._onFaultUpdated)
        # table clicked
        self.table_view.clicked.connect(self._onTableViewClicked)

    def _onFaultUpdated(self):
        distance = faultDetectionPipeline.accumulatedDistance(obj='batch')
        for fault in faultDetectionPipeline.lastFault():
            for f in fault.faults:
                fualts_string = ','.join(f.ftype[:min(len(f.ftype), 3)]) + ('...' if len(f.ftype) > 3 else '')
                sampler_name = fault.sampler

                rowCount = self.model.rowCount()
                item = QStandardItem(f'{distance:.2f}')
                item.setData(faultDetectionPipeline.batchName(), Qt.UserRole)
                self.model.setItem(rowCount, 0, item)
                self.model.setItem(rowCount, 1, QStandardItem(sampler_name))
                self.model.setItem(rowCount, 2, QStandardItem(fualts_string))




    def _onTableViewClicked(self, index):
        """ event """

        row = index.row()

        distance = self.model.item(row, 0).text()
        batchName = self.model.item(row, 0).data(Qt.UserRole)
        sensor = self.model.item(row, 1).text()
        fault = self.model.item(row, 2).text()

        if batchName is None:
            return

        view = FaultView()
        view.label = ResultLabel(parent=view)
        view.label.setResult(os.path.join(Path.OUTPUT_DIR,batchName,distance,sensor))
        view.viewLayout.addWidget(view.label)

        # mask
        w = MaskBox(parent=self.window())
        w.setWidget(widget=view)
        w.exec()
