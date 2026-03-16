from PyQt5.QtWidgets import QPushButton

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QStackedWidget, QWidget, QMessageBox,QSplitter

from .info import InfoWidget
from .project_infomation import BatchInfomationWidget
from .project_setter import BatchSettingWidget
from .camera_display_interface import CameraDisplayInterface
from .fault_overview import OnlineFaultOverview
from .lightning_interface import LightnInterface
from .enable_interface import EnableInterface
from core.pipeline import faultDetectionPipeline, LightningSerialConnectError
from ...companent.font import setFont
from ...companent import Pivot
from core.config import config


class DetectionInterface(QWidget):

    def __init__(self, parent=None):
        super(DetectionInterface, self).__init__(parent)
        self.setObjectName("DetectionInterface")

        self.initWidget()
        self.initConnect()
        self.initLayout()

    def initWidget(self):
        # 当前批次的显示
        self.faultOverview = OnlineFaultOverview(self)
        # 摄像头的原始图像和处理结果可视化
        self.cameraDisplayInterface = CameraDisplayInterface(parent=self)
        # 放电检测的数据显示
        self.lightnInterface = LightnInterface(parent=self)
        # 设备的使能窗口
        self.enableInterface = EnableInterface(parent=self)

        # info
        self.infoWidget = InfoWidget(parent=self)

        # 控制区域
        self.panel = Pivot(parent=self)
        self.w3 = QWidget(self)
        self.stack = QStackedWidget(self)
        self.batchSettingWidget = BatchSettingWidget(parent=self)
        self.batchInfomationWidget = BatchInfomationWidget(parent=self)
        self.stack.addWidget(self.batchSettingWidget)
        self.stack.addWidget(self.batchInfomationWidget)
        self.panel.addButton(text="设置", onClicked=lambda: self.stack.setCurrentWidget(self.batchSettingWidget))
        self.panel.addButton(text="结果", onClicked=lambda: self.stack.setCurrentWidget(self.batchInfomationWidget))

        # 分割
        self.splitter = QSplitter(self)
        self.splitter.setContentsMargins(0,0,0,0)

    def initConnect(self):
        pass

    def initLayout(self):
        self.w1= QWidget(self)
        self.w2 = QWidget(self)
        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.vlayout = QVBoxLayout(self.w1)
        self.hlayout1 = QHBoxLayout()
        self.hlayout1.addWidget(self.faultOverview)
        self.hlayout1.addWidget(self.lightnInterface)
        self.vlayout.addLayout(self.hlayout1)
        self.vlayout.addWidget(self.cameraDisplayInterface)
        self.vlayout.addWidget(self.infoWidget)
        self.hlayout1.setStretch(0, 3)
        self.hlayout1.setStretch(1, 0)
        self.vlayout.setStretch(0, 1)
        self.vlayout.setStretch(1, 4)

        self.settinglLayout = QVBoxLayout(self.w2)
        self.settinglLayout.addWidget(self.panel)
        self.settinglLayout.addWidget(self.stack, 1)
        self.settinglLayout.addWidget(self.enableInterface)

        self.viewLayout.addWidget(self.splitter)
        self.splitter.addWidget(self.w1)
        self.splitter.addWidget(self.w2)
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1,3)
        self.viewLayout.setStretch(0, 1)
