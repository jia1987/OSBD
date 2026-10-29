""" 底部设备状态栏 (设计稿): 8 个状态芯片 + 已检长度/线速/帧率/时钟
保留历史类名与 300ms 刷新; 运行时间移入时钟 tooltip """
from datetime import datetime

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget

from core import faultDetectionPipeline
from ..companent import Label
from ..companent.status_chip import StatusChip
from ..common import Theme


def time_diff(start_time, end_time):
    """计算两个时间的差距（天、时、分、秒）"""
    delta = end_time - start_time
    total_seconds = int(delta.total_seconds())

    days = total_seconds // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return days, hours, minutes, seconds


class BottomInfoInterface(QWidget):

    def __init__(self, parent=None):
        super(BottomInfoInterface, self).__init__(parent)
        self.setObjectName("BottomInfoInterface")
        self.setFixedHeight(36)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._onTimeOut)
        self._startTime = datetime.now()

        self.initWidget()
        self.initLayout()
        self.timer.start(300)

        self._onTimeOut()

    def initWidget(self):
        self.camera_chips = [StatusChip(text=f'相机{i + 1}', state='off', parent=self) for i in range(4)]
        self.light_chip = StatusChip(text='光源', state='off', parent=self)
        self.vsampler_chip = StatusChip(text='计米轮', state='off', parent=self)
        self.lightning_chip = StatusChip(text='放电', state='off', parent=self)
        self.iocard_chip = StatusChip(text='IO卡', state='off', parent=self)

        self.length_label = Label(text='', fontSize=12, parent=self)
        self.length_label.setStyleSheet(f'color:{Theme.TEAL};font-weight:bold;background:transparent;')
        self.velocity_label = Label(text='', fontSize=12, parent=self)
        self.velocity_label.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        self.fps_label = Label(text='', fontSize=12, parent=self)
        self.fps_label.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        self.time_label = Label(text='', fontSize=12, parent=self)
        self.time_label.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')

    def initLayout(self):
        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(16, 0, 16, 0)
        self.viewLayout.setSpacing(10)

        for chip in self.camera_chips:
            self.viewLayout.addWidget(chip)
        self.viewLayout.addWidget(self.light_chip)
        self.viewLayout.addWidget(self.vsampler_chip)
        self.viewLayout.addWidget(self.lightning_chip)
        self.viewLayout.addWidget(self.iocard_chip)
        self.viewLayout.addStretch(1)
        self.viewLayout.addWidget(self.length_label)
        self.viewLayout.addWidget(self.velocity_label)
        self.viewLayout.addWidget(self.fps_label)
        self.viewLayout.addWidget(self.time_label)

    def _onTimeOut(self):
        for idx, chip in enumerate(self.camera_chips):
            camera_ctx = faultDetectionPipeline.CHANNELS[idx]
            info = faultDetectionPipeline.channels(ctx=camera_ctx)
            chip.setState('ok' if (info is not None and info.camera is not None) else 'err')
        self.light_chip.setState('ok' if faultDetectionPipeline.isLightSourceEnabled() else 'off')
        self.vsampler_chip.setState('ok' if faultDetectionPipeline.isVSamplerEnabled() else 'off')
        self.lightning_chip.setState('ok' if faultDetectionPipeline.isLightningEnabled() else 'off')
        io = faultDetectionPipeline.IOCard()
        self.iocard_chip.setState('ok' if getattr(io, 'lib', None) is not None else 'err')

        # 总里程 (历史行为: 底部栏用 obj='all')
        self.length_label.setText(f'已检长度: {faultDetectionPipeline.accumulatedDistance():.2f} m')
        self.velocity_label.setText(f'线速: {faultDetectionPipeline.velocity():.2f} m/s')
        pt = faultDetectionPipeline.processTime()
        self.fps_label.setText(f'帧率: {int(1 / pt)} FPS' if pt and pt > 0 else '帧率: -- FPS')

        now_time = datetime.now()
        self.time_label.setText(now_time.strftime('%Y-%m-%d %H:%M:%S'))
        d, h, m, s = time_diff(self._startTime, now_time)
        self.time_label.setToolTip(f'运行时间: {d}天{h}时{m}分{s}秒')
