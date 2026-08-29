""" 设备设置页 (设计稿 P5) 组装 """
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from .device_page import DeviceSettingPage
from ...session import Session


class SettingInterface(QWidget):
    def __init__(self, parent=None):
        super(SettingInterface, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        self.page = DeviceSettingPage(self)
        layout.addWidget(self.page)
        # 权限: 工人只读 (导航已隐藏, 双保险)
        if Session.is_worker_only:
            self.page.setEnabled(False)
