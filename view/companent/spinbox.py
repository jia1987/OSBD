from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox
from .utils import loadQss
from .font import setFont


class SpinBox(QSpinBox):
    def __init__(self, paent=None):
        super(SpinBox, self).__init__(parent=paent)
        loadQss(w=self, path=r'_rc/qss/spin_box.qss')
        setFont(self)


class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, paent=None):
        super(DoubleSpinBox, self).__init__(parent=paent)
        loadQss(w=self, path=r'_rc/qss/spin_box.qss')
        setFont(self)
