""" 右侧面板: 实时缺陷统计 6 卡 + 实时缺陷列表 (自动滚最新/单击定位/双击复判)
数据沿用历史语义: faultUpdated 时遍历 lastFault() 追加 """
import os
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QTableView, QHeaderView,
                             QMessageBox)

from ...companent import MaskBox, Label
from ...companent.cards import StatCard
from ...companent.result_edit_widget import ResultEditWidget
from ...common import Theme
from core import faultDetectionPipeline
from core.const import Path
from core.signal_bus import SignalBus

STAT_TYPES = [('总缺陷', Theme.ACCENT), ('汽包', Theme.TEAL), ('粒子', Theme.ORANGE),
              ('漆瘤', Theme.YELLOW), ('毛粘线', Theme.GREEN), ('针孔·放电', Theme.RED)]


class RealtimePanel(QWidget):
    locate = pyqtSignal(str)  # ctx, 单击行定位到通道图像

    def __init__(self, parent=None):
        super(RealtimePanel, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---- 统计卡 ----
        grid = QGridLayout()
        grid.setSpacing(8)
        self._stats = {}
        for i, (name, color) in enumerate(STAT_TYPES):
            card = StatCard('0', name, color, self)
            self._stats[name] = card
            grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid)

        # ---- 实时列表 ----
        title = Label(text='实时缺陷列表', fontSize=14, weight=QFont.Bold)
        title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        layout.addWidget(title)
        self._model = QStandardItemModel(0, 5, self)
        self._model.setHorizontalHeaderLabels(['时间', '位置(m)', '通道', '类型', '置信'])
        self._table = QTableView(self)
        self._table.setModel(self._model)
        self._table.setEditTriggers(QTableView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 5):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self._table.clicked.connect(self._on_clicked)
        self._table.doubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self._table, 1)

        tip = Label(text='▲ 自动滚动 · 最新在上 · 单击定位 · 双击复判', fontSize=11)
        tip.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        layout.addWidget(tip)

        self._counts = {name: 0 for name, _ in STAT_TYPES}
        SignalBus.batchUpdated.connect(lambda *_: self._reset())
        SignalBus.faultUpdated.connect(self._on_fault_updated)

    # ================== 数据 ==================
    def _reset(self):
        self._counts = {name: 0 for name, _ in STAT_TYPES}
        self._model.removeRows(0, self._model.rowCount())
        self._refresh_stats()

    def _refresh_stats(self):
        for name, card in self._stats.items():
            card.setNum(str(self._counts[name]))

    @staticmethod
    def _channel_text(sampler: str) -> str:
        chs = faultDetectionPipeline.CHANNELS
        if sampler in chs:
            return f'通道{chs.index(sampler) + 1}'
        return '—'

    def _on_fault_updated(self):
        last = faultDetectionPipeline.lastFault()
        if not last:
            return
        distance = faultDetectionPipeline.accumulatedDistance(obj='batch')
        now = datetime.now().strftime('%H:%M:%S')
        for fi in last:
            if not fi.faults:
                continue
            for f in fi.faults:
                kind = '针孔·放电' if f.ftype == '针孔缺陷' else f.ftype
                self._counts['总缺陷'] += 1
                if kind in self._counts:
                    self._counts[kind] += 1
                self._model.insertRow(0)
                row = [now, f'{distance:.2f}', self._channel_text(fi.sampler), f.ftype,
                       f'{f.conf:.2f}' if f.conf is not None else '—']
                for c, text in enumerate(row):
                    item = QStandardItem(text)
                    item.setData(fi.sampler, Qt.UserRole)          # 定位用
                    item.setData(f'{distance:.2f}', Qt.UserRole + 1)  # 位置(目录名)
                    item.setData(f.batchName, Qt.UserRole + 2)
                    self._model.setItem(0, c, item)
        self._refresh_stats()
        self._table.scrollToTop()

    # ================== 交互 ==================
    def _on_clicked(self, index):
        sampler = self._model.item(index.row(), 0).data(Qt.UserRole)
        if sampler in faultDetectionPipeline.CHANNELS:
            self.locate.emit(sampler)

    def _on_double_clicked(self, index):
        # 沿用历史路径约定 output/{批次}/{距离}/{传感器} 打开复判
        batch = self._model.item(index.row(), 0).data(Qt.UserRole + 2)
        distance = self._model.item(index.row(), 0).data(Qt.UserRole + 1)
        sampler = self._model.item(index.row(), 0).data(Qt.UserRole)
        if batch is None:
            return
        path = os.path.join(Path.OUTPUT_DIR, batch, distance, sampler)
        if not os.path.exists(path):
            return
        box = MaskBox(self.window())
        edit = ResultEditWidget(parent=box)
        edit.setResult(path)
        box.setWidget(edit)
        box.exec_()
