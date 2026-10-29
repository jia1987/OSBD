import os.path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget, QLabel, QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtCore import Qt

from qframelesswindow import FramelessWindow

from .companent import Panel, Icon, Label, AlarmDialog
from .companent.title_bar import AppTitleBar
from core.const import Path, Text
from core.config import config
from core.signal_bus import SignalBus

from .interface import DetectionInterface, BottomInfoInterface, SettingInterface, MemoryhInterface
from .interface.system_interface import SystemInterface
from .session import Session
from .shutdown import release_devices


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
        # 设计稿标题栏 (替换默认 titleBar, 保留拖拽与窗口按钮)
        self.appTitleBar = AppTitleBar(self)
        self.setTitleBar(self.appTitleBar)

        self.panel = Panel(parent=self)
        self.detectionInterface = DetectionInterface(self)
        self.bottomInfoInterface = BottomInfoInterface(self)
        self.settingInterface = SettingInterface(self)
        self.memoryhInterface = MemoryhInterface(self)
        self.systemInterface = SystemInterface(self)

        # stackedWidget
        self.stackedWidget = QStackedWidget(self)

    def initData(self):
        self.detectBtn = self.panel.addButton(text=self.tr('实时检测'), icon=Icon.DETECTION,
                                              onClicked=lambda: self.stackedWidget.setCurrentWidget(self.detectionInterface))
        self.historyBtn = self.panel.addButton(text=self.tr('历史记录'), icon=Icon.HISTORY,
                                               onClicked=lambda: self.stackedWidget.setCurrentWidget(self.memoryhInterface))
        self.settingBtn = self.panel.addButton(text=self.tr('设备设置'), icon=Icon.SETTING,
                                               onClicked=lambda: self.stackedWidget.setCurrentWidget(self.settingInterface))
        self.systemBtn = self.panel.addButton(text=self.tr('系统设置'), icon=Icon.DARABASE,
                                              onClicked=lambda: self.stackedWidget.setCurrentWidget(self.systemInterface))
        # 权限: 工人隐藏 设备设置/系统设置
        if Session.is_worker_only:
            self.settingBtn.hide()
            self.systemBtn.hide()
        self.panel.addFooter('V2.0.0')

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        # 顶部 48px 让位给 titleBar (overlay)
        self.viewLayout.setContentsMargins(0, 48, 0, 0)
        self.contentLayout = QHBoxLayout()

        self.stackedWidget.addWidget(self.detectionInterface)
        self.stackedWidget.addWidget(self.memoryhInterface)
        self.stackedWidget.addWidget(self.settingInterface)
        self.stackedWidget.addWidget(self.systemInterface)
        self.stackedWidget.setCurrentWidget(self.detectionInterface)
        self.vlayout = QVBoxLayout()
        self.vlayout.setSpacing(0)
        self.vlayout.addWidget(self.stackedWidget, 1)
        self.vlayout.addWidget(self.bottomInfoInterface)

        self.contentLayout.addWidget(self.panel)
        self.contentLayout.addLayout(self.vlayout)
        self.contentLayout.setStretch(0, 0)
        self.contentLayout.setStretch(1, 1)

        self.viewLayout.addLayout(self.contentLayout)

        # 提升到最顶层
        self.titleBar.raise_()

        # 告警弹窗 (UI_AlarmPopup 开启时, 非模态 3s 自动关闭)
        self._alarm_dialog = AlarmDialog(self)
        SignalBus.faultUpdated.connect(self._on_fault_alarm)

    def _on_fault_alarm(self):
        if not config.get(config.UI_AlarmPopup):
            return
        from core import faultDetectionPipeline
        last = faultDetectionPipeline.lastFault()
        if not last:
            return
        lines = []
        for fi in last:
            if not fi.faults:
                continue
            types = ','.join(f.ftype for f in fi.faults)
            lines.append(f'位置 {fi.location:.2f} m 处检出缺陷: {types} ({fi.sampler})')
        if lines:
            self._alarm_dialog.showAlarm('\n'.join(lines[:3]))

    def closeEvent(self, event):
        """ 统一处理所有退出路径 (标题栏关闭/Alt+F4/系统关机),
        先释放设备并等待缺陷数据保存完成再退出 """
        release_devices()
        super(Window, self).closeEvent(event)
