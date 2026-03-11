from PyQt5.QtWidgets import QLineEdit
from .font import setFont
from .utils import loadQss


class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/line_edit.qss')
        setFont(self)