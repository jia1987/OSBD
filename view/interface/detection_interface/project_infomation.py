from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QLineEdit, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QTableView, QHeaderView
from core.signal_bus import SignalBus
from view.companent import PipelineCameraLabel, PipelineResultLabel, Label
from typing import List
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget
from core import faultDetectionPipeline
from ...companent import Label, EdgegWidget,TableView


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
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

    def _onFaultUpdated(self):
        distance = faultDetectionPipeline.accumulatedDistance(obj='batch')
        for ctx, sampler_name in zip(faultDetectionPipeline.CHANNELS, ('相机左', '相机上', '相机右', '相机下')):
            camera = faultDetectionPipeline.channels(ctx=ctx)
            if camera.faults is None: continue
            if len(camera.faults) == 0: continue
            # add item
            faults = tuple({f.ftype for f in camera.faults})
            fualts_string = ','.join(faults[:min(len(faults), 3)]) + ('...' if len(faults) > 3 else '')

            rowCount = self.model.rowCount()
            self.model.setItem(rowCount, 0, QStandardItem(f'{distance:.2f}'))
            self.model.setItem(rowCount, 1, QStandardItem(sampler_name))
            self.model.setItem(rowCount, 2, QStandardItem(fualts_string))
