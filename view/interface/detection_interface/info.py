from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QTimer
from view.companent import Label
from typing import List
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget
from core import faultDetectionPipeline


class InfoWidget(QWidget):
    """一些总体的信息显示 """
    def __init__(self, parent=None):
        super(InfoWidget, self).__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._onTimeOut)

        self.initWidget()
        self.initConnect()
        self.initLayout()

        self.timer.start(50)  # 50ms
        self._onTimeOut()

    def initWidget(self):
        self.v_label = Label(text='', fontSize=14, parent=self, )
        self.av_label = Label(text='', fontSize=14, parent=self, )
        self.process_time_label = Label(text='', fontSize=14, parent=self, )
        self.pipeline_state = Label(text='', fontSize=14, parent=self, )

    def initConnect(self):
        pass

    def initLayout(self):
        self.viewLayout = QGridLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.viewLayout.addWidget(self.v_label, 0, 0)
        self.viewLayout.addWidget(self.av_label, 1, 0)
        self.viewLayout.addWidget(self.process_time_label, 0, 1)
        self.viewLayout.addWidget(self.pipeline_state, 0, 2)

    def _onTimeOut(self):
        self.v_label.setText(self.tr('速度(m/s):') + "%.3f" % faultDetectionPipeline.velocity())
        self.av_label.setText(self.tr('角速度(转/s):') + "%.3f" % faultDetectionPipeline.angularVelocity())
        self.process_time_label.setText(self.tr('处理时间:') + "%.3f" % faultDetectionPipeline.processTime())
        self.pipeline_state.setText(self.tr('处理状态:') +  str(faultDetectionPipeline.state()))
