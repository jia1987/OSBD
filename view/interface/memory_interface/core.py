""" 历史记录页 (设计稿 P4): 左筛选+批次列表 | 中 KPI/泳道/通道图/明细表 | 右复判
沿用: output 目录结构、fault.json 读取、负责人回退、距离排序容错 """
import json
import os
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from ...companent import Label
from ...common import Theme
from core.const import Path
from core.pipeline import FaultInfo
from .center_panel import HistoryCenterPanel
from .left_panel import HistoryLeftPanel, _distance_sort_key
from .review_widget import ReviewWidget, load_review

CHANNEL_SENSOR = {1: 'c1', 2: 'c2', 3: 'c3', 4: 'c4', 5: 'lightning'}


class MemoryhInterface(QWidget):
    def __init__(self, parent=None):
        super(MemoryhInterface, self).__init__(parent)
        self._all_rows = []
        self._filtered = []
        self._current = -1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.left = HistoryLeftPanel(self)
        self.center = HistoryCenterPanel(self)
        self.right_wrap = QWidget(self)
        right_layout = QVBoxLayout(self.right_wrap)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        nav = QHBoxLayout()
        self.prev_btn = QPushButton('◀ 上一个')
        self.next_btn = QPushButton('下一个 ▶')
        self.prev_btn.clicked.connect(lambda: self._step(-1))
        self.next_btn.clicked.connect(lambda: self._step(1))
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        right_layout.addLayout(nav)
        self.review = ReviewWidget(self)
        right_layout.addWidget(self.review, 1)

        layout.addWidget(self.left, 2)
        layout.addWidget(self.center, 6)
        layout.addWidget(self.right_wrap, 3)

        self.left.batchSelected.connect(self._on_batch_selected)
        self.left.filtersChanged.connect(self._apply_filters)
        self.center.rowActivated.connect(self._on_row_activated)
        self.review.changed.connect(self._reload_current_batch)

    # ================= 扫描 =================
    def _on_batch_selected(self, name):
        self._batch = name
        self._scan(name)
        self._apply_filters()

    def _reload_current_batch(self):
        if getattr(self, '_batch', None):
            keep = self._current
            self._scan(self._batch)
            self._apply_filters()
            if 0 <= keep < len(self._filtered):
                self._on_row_activated(keep)

    def _scan(self, name):
        rows = []
        bdir = os.path.join(Path.OUTPUT_DIR, name)
        if not os.path.isdir(bdir):
            self._all_rows = rows
            return
        for dist in sorted(os.listdir(bdir), key=_distance_sort_key):
            ddir = os.path.join(bdir, dist)
            if not os.path.isdir(ddir):
                continue
            for sensor in os.listdir(ddir):
                sdir = os.path.join(ddir, sensor)
                fjson = os.path.join(sdir, 'fault.json')
                if not os.path.isfile(fjson):
                    continue
                try:
                    with open(fjson, 'r', encoding='utf-8') as f:
                        info = FaultInfo.from_dict(**json.load(f))
                except Exception as e:
                    print(f'[System] 加载缺陷记录失败 {fjson}: {e}')
                    continue
                img = os.path.join(sdir, 'image.jpg')
                mtime = os.path.getmtime(img) if os.path.isfile(img) else None
                review = load_review(sdir)
                for i, f in enumerate(info.faults):
                    rows.append({
                        'distance': dist, 'sensor': sensor, 'ftype': f.ftype,
                        'conf': getattr(f, 'conf', None), 'time': mtime,
                        'worker': info.worker, 'status': review.get(str(i), 'pending'),
                        'path': sdir, 'idx': i,
                    })
        self._all_rows = rows

    # ================= 过滤 =================
    def _apply_filters(self):
        fl = self.left.filters()
        date_from = self.left.date_from()
        rows = []
        for r in self._all_rows:
            if fl['type'] != '全部类型' and r['ftype'] != fl['type']:
                continue
            if fl['channel'] != 0 and r['sensor'] != CHANNEL_SENSOR.get(fl['channel']):
                continue
            if date_from is not None and (r['time'] is None or
                                          datetime.fromtimestamp(r['time']) < date_from):
                continue
            if not fl['with_mis'] and r['status'] == 'misreport':
                continue
            rows.append(r)
        self._filtered = rows
        self.center.set_rows(rows, getattr(self, '_batch', None))
        if rows:
            self._on_row_activated(0)
        else:
            self.review.clear()

    # ================= 选中/翻页 =================
    def _on_row_activated(self, gi):
        if not (0 <= gi < len(self._filtered)):
            return
        self._current = gi
        r = self._filtered[gi]
        self.center.select_row(gi)
        self.review.set_point(r['path'], r['distance'], r['sensor'], r['worker'])
        self.review.edit.list_widget.setCurrentRow(r['idx'])

    def _step(self, delta):
        self._on_row_activated(self._current + delta)
