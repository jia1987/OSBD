""" 底部缺陷分布总览: 5 泳道滚动窗口(最近 50m), 红=视觉缺陷 橙=放电
沿用历史跳过条件: camera None / faults None / 空 """
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from ...companent import Label, PushButton
from ...companent.lanes import LanesOverview
from ...common import Theme
from core import faultDetectionPipeline
from core.signal_bus import SignalBus

WINDOW = 50.0  # 滚动窗口: 最近 50m


class BottomLanes(QWidget):
    def __init__(self, parent=None):
        super(BottomLanes, self).__init__(parent)
        self.setFixedHeight(150)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 6)
        layout.setSpacing(4)

        head = QHBoxLayout()
        title = Label(text='缺陷分布总览 — 当前批次 (滚动窗口: 最近 50 m)', fontSize=13,
                      weight=QFont.Bold)
        title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        head.addWidget(title)
        head.addStretch(1)
        self._clear_btn = PushButton(self, text='清空显示')
        self._clear_btn.setFixedSize(80, 24)
        head.addWidget(self._clear_btn)
        layout.addLayout(head)

        self.lanes = LanesOverview(self)
        layout.addWidget(self.lanes, 1)
        self._clear_btn.clicked.connect(self.lanes.clear)

        SignalBus.batchUpdated.connect(lambda *_: self.lanes.clear())
        SignalBus.faultUpdated.connect(self._on_fault_updated)

    def _on_fault_updated(self):
        distance = faultDetectionPipeline.accumulatedDistance(obj='batch')
        for idx, ctx in enumerate(faultDetectionPipeline.CHANNELS):
            info = faultDetectionPipeline.channels(ctx=ctx)
            if info is None or info.camera is None or info.faults is None or len(info.faults) == 0:
                continue
            self.lanes.addPoint(idx, distance)
        if faultDetectionPipeline.lightningOutput().fault:
            self.lanes.addPoint(4, distance)
        self.lanes.setScope(max(0.0, distance - WINDOW), max(WINDOW, distance))
