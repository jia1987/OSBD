""" 历史记录页左栏: 搜索+筛选+批次列表
沿用: 500ms 刷新/增量同步/距离排序容错/负责人回退(DB→fault.worker→无) """
import json
import os
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem, QComboBox)

from ...companent import Label, LineEdit, ListWidget, ToggleButton, PushButton
from ...common import Theme
from core.const import Path
from core.database import UserManager
from core.pipeline import FaultInfo


def _distance_sort_key(name: str):
    """ 数值目录按升序, 非数值目录排后 (沿用历史容错) """
    try:
        return (0, float(name), name)
    except ValueError:
        return (1, 0.0, name)


class HistoryLeftPanel(QWidget):
    batchSelected = pyqtSignal(str)
    filtersChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(HistoryLeftPanel, self).__init__(parent)
        self._cache = {}  # batch -> sub text
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.searchEdit = LineEdit(self)
        self.searchEdit.setPlaceholderText('🔍 搜索批次')
        self.searchEdit.textChanged.connect(lambda *_: self.filtersChanged.emit())
        layout.addWidget(self.searchEdit)

        row1 = QHBoxLayout()
        row1.addWidget(Label(text='时间', fontSize=12))
        self.dateCombo = QComboBox(self)
        self.dateCombo.addItems(['全部时间', '今天', '近7天', '本月'])
        self.dateCombo.currentIndexChanged.connect(lambda *_: self.filtersChanged.emit())
        row1.addWidget(self.dateCombo, 1)
        layout.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(Label(text='类型', fontSize=12))
        self.typeCombo = QComboBox(self)
        self.typeCombo.addItems(['全部类型', '汽包', '粒子', '漆瘤', '毛粘线', '针孔缺陷'])
        self.typeCombo.currentIndexChanged.connect(lambda *_: self.filtersChanged.emit())
        row2.addWidget(self.typeCombo, 1)
        layout.addLayout(row2)
        row3 = QHBoxLayout()
        row3.addWidget(Label(text='通道', fontSize=12))
        self.channelCombo = QComboBox(self)
        self.channelCombo.addItems(['全部通道', '通道1', '通道2', '通道3', '通道4', '放电'])
        self.channelCombo.currentIndexChanged.connect(lambda *_: self.filtersChanged.emit())
        row3.addWidget(self.channelCombo, 1)
        layout.addLayout(row3)

        mis_row = QHBoxLayout()
        self.misToggle = ToggleButton(self)
        self.misToggle.setFixedSize(44, 24)
        self.misToggle.setChecked(True)
        self.misToggle.toogled.connect(lambda *_: self.filtersChanged.emit())
        mis_row.addWidget(self.misToggle)
        mis_row.addWidget(Label(text='包含已标误报', fontSize=12))
        mis_row.addStretch(1)
        layout.addLayout(mis_row)

        layout.addWidget(Label(text='批次列表', fontSize=13, weight=QFont.Bold))
        self.batchList = ListWidget(self)
        self.batchList.currentRowChanged.connect(self._on_row_changed)
        layout.addWidget(self.batchList, 1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_batches)
        self._timer.start(500)
        self.refresh_batches()

    # ================= 批次列表 =================
    def refresh_batches(self):
        if not self.isVisible() and self.batchList.count():
            return
        if not os.path.exists(Path.OUTPUT_DIR):
            return
        names = [n for n in os.listdir(Path.OUTPUT_DIR)
                 if os.path.isdir(os.path.join(Path.OUTPUT_DIR, n))]
        keyword = self.searchEdit.text().strip()
        if keyword:
            names = [n for n in names if keyword in n]
        names.sort(key=lambda n: os.path.getmtime(os.path.join(Path.OUTPUT_DIR, n)), reverse=True)

        current = self.currentBatch()
        self.batchList.blockSignals(True)
        # 增量同步
        while self.batchList.count() > len(names):
            self.batchList.takeItem(self.batchList.count() - 1)
        for i, name in enumerate(names):
            if i < self.batchList.count():
                item = self.batchList.item(i)
                if item.data(Qt.UserRole) != name:
                    item.setData(Qt.UserRole, name)
                    item.setText(self._sub_text(name))
            else:
                item = QListWidgetItem(self._sub_text(name))
                item.setData(Qt.UserRole, name)
                self.batchList.addItem(item)
            self.batchList.item(i).setText(self._sub_text(names[i]))
        self.batchList.blockSignals(False)
        if current and current in names:
            self.batchList.setCurrentRow(names.index(current))

    def _sub_text(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]
        bdir = os.path.join(Path.OUTPUT_DIR, name)
        worker, count, mtime = None, 0, 0
        try:
            mtime = os.path.getmtime(bdir)
            users = UserManager().getUsersByBatch(name)
            for dist in os.listdir(bdir):
                ddir = os.path.join(bdir, dist)
                if not os.path.isdir(ddir):
                    continue
                for sensor in os.listdir(ddir):
                    fjson = os.path.join(ddir, sensor, 'fault.json')
                    if not os.path.exists(fjson):
                        continue
                    try:
                        with open(fjson, 'r', encoding='utf-8') as f:
                            info = FaultInfo.from_dict(**json.load(f))
                        count += len(info.faults)
                        if worker is None:
                            worker = info.worker
                    except Exception:
                        continue
        except Exception:
            pass
        if worker is None and users:
            worker = users[0]
        text = f'{name}\n{datetime.fromtimestamp(mtime):%m-%d %H:%M} · {worker or "无"} · 缺陷{count}'
        self._cache[name] = text
        return text

    def currentBatch(self):
        item = self.batchList.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _on_row_changed(self, row):
        name = self.currentBatch()
        if name:
            self.batchSelected.emit(name)

    # ================= 筛选条件 =================
    def filters(self) -> dict:
        return {
            'date': self.dateCombo.currentIndex(),
            'type': self.typeCombo.currentText(),
            'channel': self.channelCombo.currentIndex(),
            'with_mis': self.misToggle.isChecked(),
        }

    def date_from(self):
        idx = self.dateCombo.currentIndex()
        now = datetime.now()
        if idx == 1:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        if idx == 2:
            return now - timedelta(days=7)
        if idx == 3:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return None
