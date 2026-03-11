from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QSpacerItem, QSizePolicy, QFrame
from PyQt5.QtWidgets import QScrollArea
from ...companent import Label, Pivot
from .encoder import VSamplerSettingInterface

from .camera import CameraSettingInterface
from .lightning import LightningSettingInterface
from .light_source import LightSourceSettingInterface

class SettingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initWidget()
        self.initLayout()

    def initWidget(self):
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self._w = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self._w)
        self.scrollArea.setWidgetResizable(True)

        self.vsamplerSettingInterface = VSamplerSettingInterface(parent=self, )
        self.cameraSettingInterface = CameraSettingInterface(parent=self, )
        self.lightningSettingInterface = LightningSettingInterface(parent=self, )
        self.lightSourceSettingInterface = LightSourceSettingInterface(parent=self)



    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self._wlayout = QVBoxLayout(self._w)

        self.viewLayout.addWidget(self.scrollArea)
        self._wlayout.addWidget(self.vsamplerSettingInterface)
        self._wlayout.addWidget(self.lightningSettingInterface)
        self._wlayout.addWidget(self.lightSourceSettingInterface)
        self._wlayout.addWidget(self.cameraSettingInterface)
        self._wlayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))