import time, cv2, os, json
import numpy as np
from PyQt5.QtWidgets import QLabel, QFontDialog, QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem
from PyQt5.QtGui import QPaintEvent, QPixmap, QPainter, QColor, QFontMetrics, QImage
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint, QEvent
from core import faultDetectionPipeline, ChannelInfo
from core.pipeline import FaultInfo
from core import utils
from .font import getFont
from .pipline_pixmap_label import ResultLabel
from .list_widget import ListWidget
from .combox import ComboBox
from .label import Label
from .button import PushButton, ToolButton
from functools import lru_cache
from PyQt5.QtGui import QColor


class ResultEditWidget(QWidget):
    """包含 ResultLabel + 缺陷编辑功能的完整控件"""

    def __init__(self, parent=None, vertical=False):
        super(ResultEditWidget, self).__init__(parent)
        self.closeBtn = PushButton(text=self.tr("退出"), parent=self)
        self.result_label = ResultLabel(self)
        self.result_label.installEventFilter(self)

        self.list_widget = ListWidget()
        self.type_combo = ComboBox()
        self.type_combo.setEditable(True)

        self.btn_apply = PushButton(text=self.tr("应用修改"), parent=self)

        self.info_label = Label("未选择")

        self._current_fault = None
        self._faults: FaultInfo = None

        ctrl_layout = QVBoxLayout()
        ctrl_layout.addWidget(self.closeBtn, 0, Qt.AlignRight)
        ctrl_layout.addWidget(Label("缺陷列表"))
        ctrl_layout.addWidget(self.list_widget, 1)
        ctrl_layout.addWidget(Label("修改类型"))
        ctrl_layout.addWidget(self.type_combo)
        ctrl_layout.addWidget(self.btn_apply)
        ctrl_layout.addWidget(self.info_label)
        ctrl_layout.addStretch()

        if vertical:
            # 窄栏嵌入 (历史记录右栏): 图像在上, 列表/编辑在下
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.result_label, 3)
            main_layout.addLayout(ctrl_layout, 2)
        else:
            # 宽弹窗 (复判): 图像为主, 列表/编辑列为辅
            main_layout = QHBoxLayout(self)
            main_layout.addWidget(self.result_label, 3)
            main_layout.addLayout(ctrl_layout, 1)

        # signals
        self.list_widget.itemClicked.connect(lambda item: self._select_fault(item.data(Qt.UserRole)))
        self.btn_apply.clicked.connect(self._apply_change)
        self.closeBtn.clicked.connect(self.close)

        # 连接 resultlabel 点击（通过 monkey patch）
        # self.result_label.mousePressEvent = self._label_mouse_press

    def setResult(self, path):
        """ load data """
        self.result_label.setResult(path)

        self._faults: FaultInfo = self.result_label._faults

        self.list_widget.clear()
        if self._faults:
            for i, f in enumerate(self._faults.faults):
                item = QListWidgetItem(f"{i}: {f.ftype}")
                item.setData(Qt.UserRole, f)
                self.list_widget.addItem(item)

    def eventFilter(self, obj, e):
        if e.type() == QEvent.MouseButtonRelease and obj is self.result_label:
            # faultIn 返回 -1 表示没有命中任何缺陷, 不能选中
            if self._faults is None:
                return False
            i = self.result_label.faultIn(pos=e.pos())
            if i < 0 or i >= len(self._faults.faults):
                return False
            self._select_fault(fault=self._faults.faults[i])
        return False

    def _select_fault(self, fault):
        """ select fault """
        self._current_fault = fault
        self.type_combo.setCurrentText(fault.ftype)
        self.update()

    def update(self):
        fault = self._current_fault
        if fault is not None:
            self.info_label.setText(
                f"已选择: {fault.ftype} "
                f"[{fault.x}, {fault.y}, {fault.w}, {fault.h}]"
            )
            self.info_label.update()
        super(ResultEditWidget, self).update()

    def _apply_change(self):
        """ apply change """
        if self._current_fault is None or self._faults is None: return

        new_type = self.type_combo.currentText()
        self._current_fault.ftype = new_type

        # refresh list
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            f = item.data(Qt.UserRole)
            item.setText(f"{i}: {f.ftype}")

        self.result_label.update()
        with open(os.path.join(self.result_label.readPath(), 'fault.json'), 'w', encoding='utf-8') as f:
            json.dump(self._faults.to_dict(), f, ensure_ascii=False, indent=4)
        self.result_label.setResult(path=self.result_label.readPath())
        self.update()
