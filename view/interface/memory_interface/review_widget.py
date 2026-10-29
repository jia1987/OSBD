""" 缺陷复判: review.json 旁路状态(不改 fault.json) + 复判面板
写回 fault.json 仍唯一经由 ResultEditWidget """
import json
import os
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea)

from ...companent import Label, PushButton, ResultEditWidget
from ...common import Theme

REVIEW_FILE = 'review.json'


def load_review(path: str) -> dict:
    """ {fault_index_str: 'misreport'|'confirmed'} """
    fp = os.path.join(path, REVIEW_FILE)
    if not os.path.exists(fp):
        return {}
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'[System] 加载 review.json 失败 {fp}: {e}')
        return {}


def save_review(path: str, review: dict):
    fp = os.path.join(path, REVIEW_FILE)
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(review, f, ensure_ascii=False, indent=4)


class ReviewWidget(QWidget):
    """ 右栏复判面板: 信息行 + ResultEditWidget(复用写回) + 误报标记 """
    changed = pyqtSignal()  # review 状态变化 → 刷新表格

    def __init__(self, parent=None):
        super(ReviewWidget, self).__init__(parent)
        self._path = None
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = Label(text='缺陷详情 / 复判', fontSize=14, weight=QFont.Bold)
        title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        layout.addWidget(title)

        self.info_label = QLabel('未选择缺陷点')
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            f'color:{Theme.TXT2};background:{Theme.CARD2};border:1px solid {Theme.BORDER};'
            f'border-radius:6px;padding:8px;font-size:14px;')
        layout.addWidget(self.info_label)

        # 窄栏嵌入: 纵向排布, 隐藏"退出"(仅弹窗模式需要)
        self.edit = ResultEditWidget(parent=content, vertical=True)
        self.edit.closeBtn.hide()
        layout.addWidget(self.edit, 1)

        btn_row = QHBoxLayout()
        self.misreport_btn = PushButton(self, text='标记为误报')
        self.misreport_btn.clicked.connect(self._toggle_misreport)
        self.confirm_btn = PushButton(self, text='确认缺陷')
        self.confirm_btn.clicked.connect(self._toggle_confirm)
        btn_row.addWidget(self.misreport_btn)
        btn_row.addWidget(self.confirm_btn)
        layout.addLayout(btn_row)

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def set_point(self, path: str, distance: str, sensor: str, worker: str = None):
        self._path = path
        self.edit.setResult(path)
        self.info_label.setText(
            f'位置: {distance} m · 通道: {sensor} · 负责人: {worker or "--"}\n'
            f'目录: {path}')

    def clear(self):
        self._path = None
        self.info_label.setText('未选择缺陷点')

    # ---------------- review 状态 ----------------
    def _current_index(self) -> int:
        return self.edit.list_widget.currentRow()

    def _set_status(self, status: str):
        if not self._path:
            return
        idx = self._current_index()
        if idx < 0:
            return
        review = load_review(self._path)
        key = str(idx)
        if review.get(key) == status:
            review.pop(key, None)
        else:
            review[key] = status
        save_review(self._path, review)
        self.changed.emit()

    def _toggle_misreport(self):
        self._set_status('misreport')

    def _toggle_confirm(self):
        self._set_status('confirmed')
