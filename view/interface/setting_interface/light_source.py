from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QVBoxLayout, QComboBox, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from ...companent import Label, SerialPortComboBox,SpinBox
from core import config, Serial


class LightSourceSettingInterface(QWidget):
    """ 光源设置 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initWidget()
        self.initLayout()
        self.initData()
        self.initConnect()

    def initWidget(self):
        self.titleLabel = Label(text=self.tr('光源'), weight=QFont.Bold, fontSize=32, parent=self, )
        self.port_combox = SerialPortComboBox(self)  # 端口
        self.baudrate_spinbox = SpinBox(self)  # 波特率
        self.light_level_spinbox = SpinBox(self)  # 亮度

    def initConnect(self):
        # 波特率
        self.baudrate_spinbox.valueChanged.connect(lambda v: config.set(config.LightSource_Baudrate, value=v))
        # 端口
        _func = lambda v: config.set(config.LightSource_Port, value=self.port_combox.currentText())
        self.port_combox.currentTextChanged.connect(_func)
        self.port_combox.currentIndexChanged.connect(_func)
        # 亮度
        self.light_level_spinbox.valueChanged.connect(lambda v: config.set(config.LightSource_Level, value=v))

    def initData(self):
        self.port_combox.setCurrentText(config.get(config.LightSource_Port))
        self.port_combox.addItem(config.get(config.LightSource_Port))
        self.baudrate_spinbox.setRange(0, 2 ** 31 - 1, )
        self.baudrate_spinbox.setValue(config.get(config.LightSource_Baudrate))
        self.light_level_spinbox.setRange(0, 255)
        self.light_level_spinbox.setValue(config.get(config.LightSource_Level))

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.gridLayout = QGridLayout()
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addLayout(self.gridLayout)

        for i, (name, item) in enumerate([
            ('端口号', self.port_combox),
            ('波特率', self.baudrate_spinbox),
            ('亮度', self.light_level_spinbox)
        ]):
            self.gridLayout.addWidget(Label(self.tr(name), 16), i, 0, alignment=Qt.AlignRight)
            self.gridLayout.addWidget(item, i, 1, )

        self.gridLayout.setColumnStretch(0, 0)
        self.gridLayout.setColumnStretch(1, 1)
        self.viewLayout.setStretch(0, 0)
        self.viewLayout.setStretch(1, 1)
        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
