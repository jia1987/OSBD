import time, cv2, os, json
import numpy as np
from PyQt5.QtWidgets import QLabel, QFontDialog, QWidget, QVBoxLayout, QHBoxLayout,QListWidgetItem
from PyQt5.QtGui import QPaintEvent, QPixmap, QPainter, QColor, QFontMetrics, QImage
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint
from core import faultDetectionPipeline, ChannelInfo
from core.pipeline import FaultInfo
from core import utils
from .font import getFont
from .pipline_pixmap_label import ResultLabel
from .list_widget import ListWidget
from .combox import ComboBox
from .label import Label
from .button import PushButton
from functools import lru_cache
from PyQt5.QtGui import QColor

class ResultEditWidget(QWidget):
    """包含 ResultLabel + 缺陷编辑功能的完整控件"""

    def __init__(self, parent=None):
        super(ResultEditWidget, self).__init__(parent)

        self.result_label = ResultLabel(self)

        self.list_widget = ListWidget()
        self.type_combo = ComboBox()
        self.type_combo.setEditable(True)

        self.btn_apply = PushButton(text=self.tr("应用修改"),parent=self)

        self.info_label = Label("未选择")

        self._current_fault = None
        self._faults = None

        # layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(Label("Fault List"))
        right_layout.addWidget(self.list_widget)
        right_layout.addWidget(Label("Edit Type"))
        right_layout.addWidget(self.type_combo)
        right_layout.addWidget(self.btn_apply)
        right_layout.addWidget(self.info_label)
        right_layout.addStretch()

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.result_label, 3)
        main_layout.addLayout(right_layout, 1)

        # signals
        self.list_widget.itemClicked.connect(self._on_list_click)
        self.btn_apply.clicked.connect(self._apply_change)

        # 连接 resultlabel 点击（通过 monkey patch）
        self.result_label.mousePressEvent = self._label_mouse_press

    # -------------------------
    # load data
    # -------------------------
    def setResult(self, path):
        self.result_label.setResult(path)

        self._faults = self.result_label._faults

        self.list_widget.clear()
        if self._faults:
            for i, f in enumerate(self._faults.faults):
                item = QListWidgetItem(f"{i}: {f.ftype}")
                item.setData(Qt.UserRole, f)
                self.list_widget.addItem(item)

    # -------------------------
    # click image
    # -------------------------
    def _label_mouse_press(self, event):
        self.result_label.mousePressEvent.__func__(self.result_label, event)

        if self.result_label._selected_fault:
            self._select_fault(self.result_label._selected_fault)

    # -------------------------
    # select fault
    # -------------------------
    def _select_fault(self, fault):
        self._current_fault = fault

        self.info_label.setText(
            f"Selected: {fault.ftype} "
            f"[{fault.x}, {fault.y}, {fault.w}, {fault.h}]"
        )

        self.type_combo.setCurrentText(fault.ftype)

    # -------------------------
    # list click
    # -------------------------
    def _on_list_click(self, item):
        fault = item.data(Qt.UserRole)
        self._select_fault(fault)

    # -------------------------
    # apply change
    # -------------------------
    def _apply_change(self):
        if self._current_fault is None:
            return

        new_type = self.type_combo.currentText()
        self._current_fault.ftype = new_type

        # refresh list
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            f = item.data(Qt.UserRole)
            item.setText(f"{i}: {f.ftype}")

        self.result_label.update()