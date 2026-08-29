""" 设置页表单行: 左标签 + 右控件槽 """
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from .label import Label


class FormRow(QWidget):
    def __init__(self, label_text: str = '', parent=None, label_width: int = 150):
        super(FormRow, self).__init__(parent)
        self.setFixedHeight(34)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self._label = Label(text=label_text, fontSize=13)
        self._label.setFixedWidth(label_width)
        layout.addWidget(self._label)
        self._slot = QHBoxLayout()
        self._slot.setSpacing(8)
        layout.addLayout(self._slot, 1)

    def setWidget(self, widget):
        self._slot.addWidget(widget)
        return widget

    def setLayout_(self, layout):
        self._slot.addLayout(layout)
