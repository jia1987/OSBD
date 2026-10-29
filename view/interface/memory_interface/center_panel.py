""" 历史记录页中栏: 批次 KPI + 全距泳道 + 4 通道缺陷图 + 明细分页表(状态/导出) """
import csv
import os
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableView,
                             QHeaderView, QFileDialog, QMessageBox)

from ...companent import Label, PushButton, ResultLabel
from ...companent.cards import KpiCard
from ...companent.lanes import LanesOverview
from ...common import Theme
from core import faultDetectionPipeline

PAGE_SIZE = 50
SENSOR_LANE = {'c1': 0, 'c2': 1, 'c3': 2, 'c4': 3, 'lightning': 4}


class HistoryCenterPanel(QWidget):
    rowActivated = pyqtSignal(int)  # 全局行索引(过滤后)

    def __init__(self, parent=None):
        super(HistoryCenterPanel, self).__init__(parent)
        self._rows = []
        self._page = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---- KPI ----
        kpi = QHBoxLayout()
        kpi.setSpacing(10)
        self.kpi_batch = KpiCard('当前批次', '--', '', Theme.TXT, self)
        self.kpi_total = KpiCard('总缺陷', '0', '个', Theme.RED, self)
        self.kpi_len = KpiCard('检测长度', '--', 'm', Theme.TEAL, self)
        self.kpi_density = KpiCard('缺陷密度', '--', '/100m', Theme.YELLOW, self)
        self.kpi_lightning = KpiCard('放电针孔', '0', '个', Theme.ORANGE, self)
        self.kpi_mis = KpiCard('误报标记', '0', '个', Theme.TXT2, self)
        for k in (self.kpi_batch, self.kpi_total, self.kpi_len,
                  self.kpi_density, self.kpi_lightning, self.kpi_mis):
            kpi.addWidget(k)
        layout.addLayout(kpi)

        # ---- 泳道 ----
        lanes_card = QVBoxLayout()
        lanes_title = Label(text='批次缺陷分布总览 (红=视觉缺陷 橙=放电)', fontSize=13, weight=QFont.Bold)
        lanes_title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        lanes_card.addWidget(lanes_title)
        self.lanes = LanesOverview(self)
        lanes_card.addWidget(self.lanes, 1)
        lanes_wrap = QWidget(self)
        lanes_wrap.setStyleSheet(f'background:{Theme.CARD};border:1px solid {Theme.BORDER};border-radius:8px;')
        lanes_wrap.setLayout(lanes_card)
        lanes_card.setContentsMargins(12, 8, 12, 6)
        layout.addWidget(lanes_wrap)

        # ---- 4 通道图 ----
        imgs = QHBoxLayout()
        imgs.setSpacing(10)
        self.channel_labels = []
        for i in range(4):
            box = QVBoxLayout()
            head = Label(text=f'通道{i + 1}', fontSize=12, weight=QFont.Bold)
            head.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
            head.setAlignment(Qt.AlignCenter)
            lbl = ResultLabel(parent=self)
            lbl.setMinimumHeight(180)
            lbl.setStyleSheet(f'background:{Theme.IMAGE};border:1px solid {Theme.BORDER};border-radius:6px;')
            lbl.clicked.connect(self._on_image_clicked(lbl))
            self.channel_labels.append(lbl)
            box.addWidget(head)
            box.addWidget(lbl, 1)
            imgs.addLayout(box, 1)
        layout.addLayout(imgs)

        # ---- 明细表 ----
        head_row = QHBoxLayout()
        t = Label(text='缺陷明细', fontSize=13, weight=QFont.Bold)
        t.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        head_row.addWidget(t)
        head_row.addStretch(1)
        self.export_btn = PushButton(self, text='导出CSV')
        self.export_btn.setFixedSize(96, 28)
        self.export_btn.clicked.connect(self.export_csv)
        head_row.addWidget(self.export_btn)
        layout.addLayout(head_row)

        self._model = QStandardItemModel(0, 7, self)
        self._model.setHorizontalHeaderLabels(['#', '时间', '位置(m)', '通道', '缺陷类型', '状态', '操作'])
        self._table = QTableView(self)
        self._table.setModel(self._model)
        self._table.setEditTriggers(QTableView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.clicked.connect(self._on_table_clicked)
        layout.addWidget(self._table, 1)

        # ---- 分页 ----
        foot = QHBoxLayout()
        self.page_label = Label(text='', fontSize=12)
        self.page_label.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        foot.addWidget(self.page_label)
        foot.addStretch(1)
        self.prev_btn = PushButton(self, text='◀ 上一页')
        self.prev_btn.setFixedSize(98, 28)
        self.next_btn = PushButton(self, text='下一页 ▶')
        self.next_btn.setFixedSize(98, 28)
        self.prev_btn.clicked.connect(lambda: self._goto(self._page - 1))
        self.next_btn.clicked.connect(lambda: self._goto(self._page + 1))
        foot.addWidget(self.prev_btn)
        foot.addWidget(self.next_btn)
        layout.addLayout(foot)

    # ================= 数据 =================
    def set_rows(self, rows, batch_name: str):
        self._rows = rows
        self._page = 0
        self._refresh_kpi(batch_name)
        self._refresh_lanes()
        self._refresh_images()
        self._refresh_table()

    def _refresh_kpi(self, batch_name):
        total = len(self._rows)
        mis = sum(1 for r in self._rows if r['status'] == 'misreport')
        lightning = sum(1 for r in self._rows if r['sensor'] == 'lightning')
        lengths = [float(r['distance']) for r in self._rows if _is_num(r['distance'])]
        length = max(lengths) if lengths else 0.0
        self.kpi_batch.setValue(batch_name or '--')
        self.kpi_total.setValue(str(total))
        self.kpi_len.setValue(f'{length:.1f}')
        self.kpi_density.setValue(f'{total / length * 100:.1f}' if length > 0 else '--')
        self.kpi_lightning.setValue(str(lightning))
        self.kpi_mis.setValue(str(mis))

    def _refresh_lanes(self):
        self.lanes.clear()
        lengths = [float(r['distance']) for r in self._rows if _is_num(r['distance'])]
        max_d = max(lengths) if lengths else 1.0
        for r in self._rows:
            lane = SENSOR_LANE.get(r['sensor'])
            if lane is None or not _is_num(r['distance']):
                continue
            self.lanes.addPoint(lane, float(r['distance']))
        self.lanes.setScope(0.0, max(max_d, 1.0))

    def _refresh_images(self):
        shown = set()
        for lbl in self.channel_labels:
            lbl.setResult(None)
        for r in self._rows:
            i = {'c1': 0, 'c2': 1, 'c3': 2, 'c4': 3}.get(r['sensor'])
            if i is None or i in shown:
                continue
            shown.add(i)
            self.channel_labels[i].setResult(r['path'])

    def _on_image_clicked(self, lbl):
        def handler(*_):
            i = self.channel_labels.index(lbl)
            sensor = f'c{i + 1}'
            for gi, r in enumerate(self._rows):
                if r['sensor'] == sensor:
                    self.rowActivated.emit(gi)
                    return
        return handler

    # ================= 表格 =================
    def _refresh_table(self):
        pages = max(1, (len(self._rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        self._page = min(self._page, pages - 1)
        start = self._page * PAGE_SIZE
        view = self._rows[start:start + PAGE_SIZE]
        self._model.removeRows(0, self._model.rowCount())
        status_cn = {'misreport': '误报', 'confirmed': '已确认', 'pending': '待复判'}
        for gi, r in enumerate(view, start=start):
            ts = datetime.fromtimestamp(r['time']).strftime('%m-%d %H:%M:%S') if r['time'] else '--'
            values = [str(gi + 1), ts, r['distance'], _channel_text(r['sensor']), r['ftype'],
                      status_cn.get(r['status'], '待复判'), '[ 复判 ]']
            self._model.appendRow([_item(v, gi) for v in values])
        self.page_label.setText(f'共 {len(self._rows)} 条 · 第 {self._page + 1} / {pages} 页')

    def _on_table_clicked(self, index):
        gi = self._model.item(index.row(), 0).data(Qt.UserRole)
        if gi is not None:
            self.rowActivated.emit(gi)

    def _goto(self, page):
        pages = max(1, (len(self._rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        self._page = max(0, min(page, pages - 1))
        self._refresh_table()

    def select_row(self, gi: int):
        """ 外部翻页联动: 跳到对应页并选中 """
        page = gi // PAGE_SIZE
        if page != self._page:
            self._page = page
            self._refresh_table()
        self._table.selectRow(gi % PAGE_SIZE)

    # ================= 导出 =================
    def export_csv(self):
        if not self._rows:
            return
        path, _ = QFileDialog.getSaveFileName(self.window(), '导出CSV', '缺陷明细.csv',
                                              'CSV Files (*.csv)')
        if not path:
            return
        status_cn = {'misreport': '误报', 'confirmed': '已确认', 'pending': '待复判'}
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                w = csv.writer(f)
                w.writerow(['位置(m)', '通道', '缺陷类型', '置信度', '状态', '负责人', '目录'])
                for r in self._rows:
                    w.writerow([r['distance'], _channel_text(r['sensor']), r['ftype'],
                                r['conf'] if r['conf'] is not None else '',
                                status_cn.get(r['status'], '待复判'), r.get('worker') or '',
                                r['path']])
            QMessageBox.information(self.window(), '成功', f'已导出 {len(self._rows)} 条记录')
        except Exception as e:
            QMessageBox.warning(self.window(), '错误', str(e))


def _item(text, gi):
    item = QStandardItem(text)
    item.setData(gi, Qt.UserRole)
    return item


def _is_num(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _channel_text(sensor):
    chs = faultDetectionPipeline.CHANNELS
    if sensor in chs:
        return f'通道{chs.index(sensor) + 1}'
    return '放电' if sensor == 'lightning' else sensor
