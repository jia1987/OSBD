import os.path

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget, QLabel, QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtSvg import QSvgWidget

from qframelesswindow import FramelessWindow

from .companent import Panel, Icon,Label
from core.const import Path,Text
from core.pipeline import faultDetectionPipeline

from .interface import DetectionInterface, BottomInfoInterface, SettingInterface,MemoryhInterface,UserManagerInterface


class Window(FramelessWindow):
    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        self.setWindowIcon(QIcon(os.path.join(Path.ICON, 'logo.svg')))
        self.setWindowTitle(self.tr(Text.APP_NAME))
        self.setMinimumSize(1200, 800)

        self.initWidget()
        self.initLayout()
        self.initData()

    def initWidget(self):
        self.iconLabel = QSvgWidget(self)
        self.iconLabel.load(os.path.join(Path.ICON,'logo.svg'))
        self.iconLabel.setFixedSize(24, 24)
        self.titleLabel = Label(parent=self,text=self.tr(Text.APP_NAME),fontSize=16,weight=QFont.Normal)

        self.panel = Panel(parent=self)
        self.detectionInterface = DetectionInterface(self)
        self.bottoImnfoInterface = BottomInfoInterface(self)
        self.settingInterface = SettingInterface(self)
        self.memoryhInterface = MemoryhInterface(self)
        self.userManagerInterface = UserManagerInterface(self)

        # stackedWidget
        self.stackedWidget = QStackedWidget(self)

    def initData(self):
        self.panel.addButton(text=self.tr('检测'), icon=Icon.DETECTION,
                             onClicked=lambda: self.stackedWidget.setCurrentWidget(self.detectionInterface))
        self.panel.addButton(text=self.tr('设置'), icon=Icon.SETTING,
                             onClicked=lambda: self.stackedWidget.setCurrentWidget(self.settingInterface)                             )
        self.panel.addButton(text=self.tr('记录'), icon=Icon.HISTORY,
                             onClicked=lambda: self.stackedWidget.setCurrentWidget(self.memoryhInterface))
        self.panel.addButton(text=self.tr('数据库'), icon=Icon.DARABASE,
                             onClicked=lambda: self.stackedWidget.setCurrentWidget(self.userManagerInterface))

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(5, 5, 5, 5)
        self.titleLayout = QHBoxLayout()
        self.contentLayout = QHBoxLayout()

        self.titleLayout.addWidget(self.iconLabel)
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addSpacerItem(QSpacerItem(0,0,QSizePolicy.Expanding,QSizePolicy.Minimum))

        self.stackedWidget.addWidget(self.detectionInterface)
        self.stackedWidget.addWidget(self.settingInterface)
        self.stackedWidget.addWidget(self.memoryhInterface)
        self.stackedWidget.addWidget(self.userManagerInterface)
        self.stackedWidget.setCurrentWidget(self.detectionInterface)
        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.stackedWidget)
        self.vlayout.addWidget(self.bottoImnfoInterface)

        self.contentLayout.addWidget(self.panel)
        self.contentLayout.addLayout(self.vlayout)
        self.contentLayout.setStretch(0, 0)
        self.contentLayout.setStretch(1, 1)

        self.viewLayout.addLayout(self.titleLayout)
        self.viewLayout.addLayout(self.contentLayout)

        # 提升到最顶层
        self.titleBar.raise_()

    def closeEvent(self, event):
        """ 统一处理所有退出路径 (标题栏关闭/Alt+F4/系统关机),
        先释放设备并等待缺陷数据保存完成再退出 """
        try:
            if faultDetectionPipeline.isDetectEnabled():
                faultDetectionPipeline.setDetectEnable(False)
            if faultDetectionPipeline.isCameraEnabled():
                faultDetectionPipeline.setCameraEnabled(False)
            if faultDetectionPipeline.isLightSourceEnabled():
                faultDetectionPipeline.setLightSourceEnable(False)
            if faultDetectionPipeline.isVSamplerEnabled():
                faultDetectionPipeline.setVSamplerEnabled(False)
            if faultDetectionPipeline.isLightningEnabled():
                faultDetectionPipeline.setLightningEnabled(False)
        except Exception as e:
            print(f'[System] 退出时释放设备失败: {e}')
        try:
            # 等待保存线程排空, 避免缺陷数据丢失
            faultDetectionPipeline.waitSaveFinished(timeout=10)
        except Exception as e:
            print(f'[System] 退出时等待保存失败: {e}')
        super(Window, self).closeEvent(event)
