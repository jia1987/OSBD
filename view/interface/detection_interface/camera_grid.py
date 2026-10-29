""" 实时检测页 2×2 通道图像网格: 状态点+通道名+原始图/结果图分段+放大
复用 PipelineCameraLabel/PipelineResultLabel 的 33ms 刷新与点击放大(活画面) """
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QGridLayout)

from ...companent import (PipelineCameraLabel, PipelineResultLabel, MaskBox, PushButton, Label)
from ...companent.font import getFont
from ...companent.segmented import SegmentedControl
from ...common import Theme
from core import faultDetectionPipeline
from .fault_view import FaultView

CHANNEL_FACES = {'c1': '左面', 'c2': '上面', 'c3': '右面', 'c4': '下面'}


class ChannelImageCard(QWidget):
    def __init__(self, ctx: str, idx: int, parent=None):
        super(ChannelImageCard, self).__init__(parent)
        self._ctx = ctx
        self._flash_until = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---- 头部 ----
        header = QWidget(self)
        header.setFixedHeight(36)
        header.setStyleSheet(f'background:{Theme.CARD2};border-radius:6px;')
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 0, 8, 0)
        h.setSpacing(8)
        self._dot = QWidget(header)
        self._dot.setFixedSize(10, 10)
        h.addWidget(self._dot)
        self._title = Label(text=f'通道{idx + 1} · {CHANNEL_FACES.get(ctx, "")}', fontSize=13,
                            weight=QFont.Bold)
        self._title.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        h.addWidget(self._title)
        h.addStretch(1)
        self._seg = SegmentedControl(['原始图', '结果图'], header, active=1, item_width=72, height=26)
        h.addWidget(self._seg)
        self._zoom_btn = PushButton(header, text='放大')
        self._zoom_btn.setFixedSize(62, 28)
        h.addWidget(self._zoom_btn)
        outer.addWidget(header)

        # ---- 画面 ----
        self._stack = QStackedWidget(self)
        self.camera_label = PipelineCameraLabel(ctx=ctx, parent=self)
        self.result_label = PipelineResultLabel(ctx=ctx, parent=self)
        self._stack.addWidget(self.camera_label)
        self._stack.addWidget(self.result_label)
        self._stack.setCurrentIndex(1)
        outer.addWidget(self._stack, 1)

        self._seg.indexChanged.connect(self._stack.setCurrentIndex)
        self._zoom_btn.clicked.connect(lambda: self._open_zoom(type(self._current_label())))
        self.camera_label.clicked.connect(lambda *_: self._open_zoom(PipelineCameraLabel))
        self.result_label.clicked.connect(lambda *_: self._open_zoom(PipelineResultLabel))

        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._maybe_unflash)

    def _current_label(self):
        return self._stack.currentWidget()

    def _open_zoom(self, label_cls):
        """ 沿用历史行为: 新建同类型同通道活画面放大 """
        box = MaskBox(self.window())
        view = FaultView(parent=box)
        view.viewLayout.addWidget(label_cls(ctx=self._ctx, parent=view))
        box.setWidget(view)
        box.exec_()

    def flash(self):
        """ 列表点击定位: 2 秒边框高亮 """
        self._flash_until = 1
        self.update()
        self._flash_timer.start(2000)

    def _maybe_unflash(self):
        self._flash_until = 0
        self._flash_timer.stop()
        self.update()

    def refresh_state(self):
        info = faultDetectionPipeline.channels(ctx=self._ctx)
        online = info is not None and info.camera is not None
        self._dot.setStyleSheet(
            f'background:{Theme.GREEN if online else Theme.RED};border-radius:5px;')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(Theme.BORDER if not self._flash_until else Theme.ACCENT),
                            1 if not self._flash_until else 3))
        painter.setBrush(QColor(Theme.CARD))
        painter.drawRoundedRect(0, 0, self.width() - 1, self.height() - 1, 6, 6)


class CameraGrid(QWidget):
    def __init__(self, parent=None):
        super(CameraGrid, self).__init__(parent)
        self.cards = {}
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        for i, ctx in enumerate(faultDetectionPipeline.CHANNELS):
            card = ChannelImageCard(ctx=ctx, idx=i, parent=self)
            self.cards[ctx] = card
            grid.addWidget(card, i // 2, i % 2)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_states)
        self._timer.start(1000)
        self._refresh_states()

    def flash(self, ctx: str):
        card = self.cards.get(ctx)
        if card is not None:
            card.flash()

    def _refresh_states(self):
        for card in self.cards.values():
            card.refresh_state()
