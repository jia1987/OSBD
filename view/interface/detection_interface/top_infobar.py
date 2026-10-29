""" 实时检测页顶部信息条: 批次/负责人卡(点击换批次) + 型号管理入口 + 5 KPI """
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

from ...companent import MaskBox, PushButton
from ...companent.cards import KpiCard
from ...companent.dialogs import BatchSwitchDialog
from ...companent.font import getFont
from ..._global import Function
from ...common import Theme
from core import faultDetectionPipeline
from core.signal_bus import SignalBus


class TopInfoBar(QWidget):
    def __init__(self, parent=None):
        super(TopInfoBar, self).__init__(parent)
        self.setFixedHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---- 批次/负责人 卡 ----
        self._batch_card = QWidget(self)
        self._batch_card.setFixedWidth(430)
        self._batch_card.setStyleSheet(
            f'background:{Theme.CARD};border:1px solid {Theme.BORDER};border-radius:8px;')
        card_layout = QHBoxLayout(self._batch_card)
        card_layout.setContentsMargins(14, 6, 14, 6)
        card_layout.setSpacing(0)
        self._batch_label = self._kv(card_layout, '当前批次', '--')
        self._sep(card_layout)
        self._worker_label = self._kv(card_layout, '负责人', '--')
        self._sep(card_layout)
        self._model_label = self._kv(card_layout, '型号', '--')
        layout.addWidget(self._batch_card)

        self._no_batch_tip = QLabel('未设置批次, 缺陷将不保存', self)
        self._no_batch_tip.setFont(getFont(11, True))
        self._no_batch_tip.setStyleSheet(
            f'color:{Theme.YELLOW};background:#33290F;border:1px solid {Theme.YELLOW};'
            f'border-radius:6px;padding:4px 10px;')
        layout.addWidget(self._no_batch_tip, 0, Qt.AlignVCenter)

        self._switch_btn = PushButton(self, text='更换批次')
        self._switch_btn.setFixedHeight(32)
        self._switch_btn.clicked.connect(self._open_batch_switch)
        layout.addWidget(self._switch_btn)

        self._model_btn = PushButton(self, text='型号/批次管理')
        self._model_btn.setFixedHeight(32)
        self._model_btn.clicked.connect(self._open_model_setting)
        layout.addWidget(self._model_btn)
        layout.addStretch(1)

        # ---- KPI ----
        self.kpi_velocity = KpiCard('线速', '--', 'm/s', Theme.ACCENT, self)
        self.kpi_batch_len = KpiCard('批次长度', '--', 'm', Theme.TEAL, self)
        self.kpi_total_len = KpiCard('累计已检', '--', 'm', Theme.TXT, self)
        self.kpi_faults = KpiCard('缺陷数', '0', '个', Theme.RED, self)
        self.kpi_time = KpiCard('单帧耗时', '--', 'ms', Theme.TXT2, self)
        for k in (self.kpi_velocity, self.kpi_batch_len, self.kpi_total_len,
                  self.kpi_faults, self.kpi_time):
            k.setFixedWidth(150)
            layout.addWidget(k)

        self._fault_count = 0
        SignalBus.batchUpdated.connect(self._on_batch_updated)
        SignalBus.faultUpdated.connect(self._on_fault_updated)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(300)
        self._on_batch_updated(None, None)
        self._refresh()

    # ---------------- helpers ----------------
    def _kv(self, layout, title, value):
        box = QVBoxLayout()
        box.setSpacing(0)
        t = QLabel(title)
        t.setFont(getFont(10))
        t.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        v = QLabel(value)
        v.setFont(getFont(14, True))
        v.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        box.addWidget(t)
        box.addWidget(v)
        layout.addLayout(box, 1)
        return v

    def _sep(self, layout):
        s = QLabel('')
        s.setFixedWidth(1)
        s.setStyleSheet(f'background:{Theme.BORDER};')
        layout.addWidget(s)

    # ---------------- slots ----------------
    def _on_batch_updated(self, batch, worker):
        b = faultDetectionPipeline.batchName()
        w = faultDetectionPipeline.workerName()
        self._batch_label.setText(b or '--')
        self._worker_label.setText(w or '--')
        self._no_batch_tip.setVisible(not b)
        self._fault_count = 0
        self.kpi_faults.setValue('0')

    def _on_fault_updated(self):
        last = faultDetectionPipeline.lastFault()
        n = 0
        if last:
            for fi in last:
                if fi.faults:
                    n += len(fi.faults)
        self._fault_count += n
        self.kpi_faults.setValue(str(self._fault_count))

    def _refresh(self):
        self.kpi_velocity.setValue(f'{faultDetectionPipeline.velocity():.2f}')
        self.kpi_batch_len.setValue(f'{faultDetectionPipeline.accumulatedDistance(obj="batch"):.2f}')
        self.kpi_total_len.setValue(f'{faultDetectionPipeline.accumulatedDistance(obj="all"):.1f}')
        pt = faultDetectionPipeline.processTime()
        self.kpi_time.setValue(f'{pt * 1000:.0f}' if pt else '--')
        mc = faultDetectionPipeline.modelConfig()
        self._model_label.setText('已配置' if mc is not None else '--')

    def _open_model_setting(self):
        from .project_setter import BatchSettingWidget
        box = MaskBox(self.window())
        box.setWidget(BatchSettingWidget(parent=box))
        box.exec_()

    def _open_batch_switch(self):
        from PyQt5.QtWidgets import QDialog
        dlg = BatchSwitchDialog(self.window())
        if dlg.exec_() == QDialog.Accepted:
            Function.swapBatch(batchName=dlg.batchName(), wokerName=dlg.workerName())
