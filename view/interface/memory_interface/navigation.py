import os

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from core.const import Path
from core.database import UserManager
from ...companent import Label, ListView

from core.pipeline import FaultInfo
import json
class Navigation(QWidget):
    """ 显示保存的所有批次, 并可以选择缺陷点并展示"""
    faultLoadRequsted = pyqtSignal(str)
    faultSetUpdated = pyqtSignal(str)

    BATCH_NAME_TAG = '批次:'
    USER_NAME_TAG = '负责人:'

    def __init__(self, parent=None):
        self._check_batch_name = None
        self._manager = UserManager()
        super().__init__(parent)

        self.initWidget()
        self.initLayout()
        self.initConnect()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._onTimeout)
        self._timer.start(500)  # 500ms

    def initWidget(self):
        self.batch_label = Label(text=self.BATCH_NAME_TAG, parent=self, fontSize=20, weight=QFont.Bold)
        self.user_label = Label(text=self.USER_NAME_TAG, parent=self, fontSize=20, weight=QFont.Bold)
        self.batch_list = ListView(self)
        self.batch_list.setModel(QStandardItemModel())
        self.batch_list.setEditTriggers(QListView.NoEditTriggers)
        self.result_list = ListView(self)
        self.result_list.setModel(QStandardItemModel())
        self.result_list.setEditTriggers(QListView.NoEditTriggers)

    def initLayout(self):
        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.hLayout1 = QHBoxLayout()

        self.vLayout1 = QVBoxLayout()
        self.vLayout2 = QVBoxLayout()

        self.viewLayout.addLayout(self.vLayout1)
        self.vLayout1.addWidget(self.batch_label)
        self.vLayout1.addWidget(self.user_label)
        self.vLayout1.addLayout(self.hLayout1)
        self.hLayout1.addWidget(self.batch_list)

        self.hLayout1.addWidget(self.result_list)

    def initConnect(self):
        self.batch_list.clicked.connect(self._on_batch_list_clicked)
        self.result_list.clicked.connect(self._on_result_list_clicked)

    def _onTimeout(self):
        self._update_all_list()

    def _update_all_list(self):
        """ 更新所有list """
        if not self.isVisible(): return
        # updage list
        if not os.path.exists(Path.OUTPUT_DIR): return

        # 同步
        self._update_list(list_view=self.batch_list, items=os.listdir(Path.OUTPUT_DIR))
        if self._check_batch_name is not None:
            read_dir = os.path.join(Path.OUTPUT_DIR, self._check_batch_name)
            items = os.listdir(read_dir)
            items = list(set(items))
            items = sorted(items, key=lambda item: float(item))
            self._update_list(list_view=self.result_list, items=items)


    def _update_list(self, list_view, items):
        """ 根据一个 path 更新 listView"""
        # 同步
        model: QStandardItemModel = list_view.model()
        idx = -1
        for idx, name in enumerate(items):
            if idx < model.rowCount():
                model.item(idx, 0).setText(name)
            else:
                model.appendRow(QStandardItem(name))
        while idx != model.rowCount() - 1:
            model.removeRow(idx)

    def _on_batch_list_clicked(self, index):
        """ 点击 """
        model: QStandardItemModel = self.batch_list.model()
        item = model.itemFromIndex(index)

        username = self._manager.getUsersByBatch(batchName=item.text())

        batchp = os.path.join(Path.OUTPUT_DIR,  item.text())
        a_fp = tuple(os.listdir(batchp))  # 0.0 0.1 0.3
        if len(a_fp) != 0:
            a_fp = a_fp[0]
            # fault
            a_f = tuple(os.listdir(os.path.join(batchp, a_fp)))
            if len(a_f) != 0:
                a_f = a_f[0]
                fault_path = os.path.join(batchp, a_fp, a_f, 'fault.json')
                if os.path.exists(fault_path):
                    with open(fault_path, "r", encoding="utf-8") as f:
                        fault = FaultInfo.from_dict(**json.load(f))
                        username = fault.worker



        self.batch_label.setText(self.tr(self.BATCH_NAME_TAG) + ' ' + item.text())
        self.user_label.setText(self.tr(self.USER_NAME_TAG) + ' ' + (username or '无'))
        self._check_batch_name = item.text()
        self._update_all_list()
        # 发送型号
        read_dir = os.path.join(Path.OUTPUT_DIR, self._check_batch_name)
        self.faultSetUpdated.emit(read_dir)

    def _on_result_list_clicked(self, index):
        """ 点击 """
        model: QStandardItemModel = self.result_list.model()
        item = model.itemFromIndex(index)
        path = os.path.join(Path.OUTPUT_DIR, self._check_batch_name, item.text())

        self.faultLoadRequsted.emit(path)

    def showEvent(self, event):
        self._update_all_list()
        super(Navigation, self).showEvent(event)
