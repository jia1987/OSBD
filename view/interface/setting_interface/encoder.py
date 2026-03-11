from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QVBoxLayout, QComboBox, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from ...companent import Label, SerialPortComboBox,SpinBox,DoubleSpinBox,ToggleButton
from core import config, Serial




class VSamplerSettingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initWidget()
        self.initLayout()
        self.initData()
        self.initConnect()

    def initWidget(self):
        self.titleLabel = Label(text=self.tr('测速编码器'), weight=QFont.Bold, fontSize=32, parent=self, )

        self.port_combox = SerialPortComboBox(self)
        self.baudrate_spinbox = SpinBox(self)
        self.perimeter_spinbox = DoubleSpinBox(self)
        self.directionToggleBtn = ToggleButton(self)

    def initConnect(self):
        self.baudrate_spinbox.valueChanged.connect(lambda v: config.set(config.VSampler_Baudrate, value=v))
        self.perimeter_spinbox.valueChanged.connect(lambda v: config.set(config.VSampler_Perimeter, value=v / 100))
        self.port_combox.currentTextChanged.connect(
            lambda v: config.set(config.VSampler_Port, value=self.port_combox.currentText()))
        self.port_combox.currentIndexChanged.connect(
            lambda v: config.set(config.VSampler_Port, value=self.port_combox.currentText()))
        self.directionToggleBtn.toogled.connect(lambda v: config.set(config.VSampler_Direction, value=v))
    def initData(self):
        self.port_combox.setCurrentText(config.get(config.VSampler_Port))
        self.port_combox.addItem(config.get(config.VSampler_Port))
        self.baudrate_spinbox.setRange(0, 2 ** 31 - 1, )
        self.baudrate_spinbox.setValue(config.get(config.VSampler_Baudrate))
        self.perimeter_spinbox.setRange(0, 2 ** 31 - 1)
        self.perimeter_spinbox.setValue(config.get(item=config.VSampler_Perimeter))
        self.perimeter_spinbox.setSingleStep(0.01)
        self.directionToggleBtn.setChecked(config.get(config.VSampler_Direction))

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.gridLayout = QGridLayout()
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addLayout(self.gridLayout)

        for i, (name, item) in enumerate([
            ('端口号', self.port_combox),
            ('波特率', self.baudrate_spinbox),
            ('单圈周长(cm)', self.perimeter_spinbox),
            ('是否反向', self.directionToggleBtn)
        ]):
            self.gridLayout.addWidget(Label(self.tr(name), 16), i, 0, alignment=Qt.AlignRight)
            self.gridLayout.addWidget(item, i, 1, )

        self.gridLayout.setColumnStretch(0, 0)
        self.gridLayout.setColumnStretch(1, 1)
        self.viewLayout.setStretch(0, 0)
        self.viewLayout.setStretch(1, 1)
        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _onProtComboxClicked(self):
        print(Serial.posts())
