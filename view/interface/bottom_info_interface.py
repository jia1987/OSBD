from ..companent import Label
from datetime import datetime

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QHBoxLayout, QWidget

from core import faultDetectionPipeline
from ..companent import Label


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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._onTimeOut)
        self._startTime = datetime.now()

        self.initWidget()
        self.initLayout()
        self.timer.start(300)  # 1000ms

        self._onTimeOut()

    def initWidget(self):
        self.vsamper_label = Label(text='', fontSize=12, parent=self, )
        self.camera_0_label = Label(text='', fontSize=12, parent=self, )
        self.camera_1_label = Label(text='', fontSize=12, parent=self, )
        self.camera_2_label = Label(text='', fontSize=12, parent=self, )
        self.camera_3_label = Label(text='', fontSize=12, parent=self, )
        self.run_time_label = Label(text='', fontSize=12, parent=self, )
        self.length_label = Label(text='', fontSize=12, parent=self, )
        self.time_label = Label(text='', fontSize=12, parent=self, )

    def initLayout(self):
        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(32)

        self.viewLayout.addWidget(self.camera_0_label)
        self.viewLayout.addWidget(self.camera_1_label)
        self.viewLayout.addWidget(self.camera_2_label)
        self.viewLayout.addWidget(self.camera_3_label)
        self.viewLayout.addWidget(self.vsamper_label)
        self.viewLayout.addWidget(self.length_label)
        self.viewLayout.addWidget(self.run_time_label)
        self.viewLayout.addWidget(self.time_label)

    def _onTimeOut(self):
        # whether connect with camera
        is_connect_title = {True: self.tr('已连接'), False: self.tr('未连接')}
        for idx, (label, prefix) in enumerate((
                (self.camera_0_label, self.tr('相机1:')),
                (self.camera_1_label, self.tr('相机2:')),
                (self.camera_2_label, self.tr('相机3:')),
                (self.camera_3_label, self.tr('相机4:')),
        )):
            camera_ctx = faultDetectionPipeline.CHANNELS[idx]
            label.setText(prefix + is_connect_title[faultDetectionPipeline.channels(ctx=camera_ctx).camera is not None])
        # whether connect with vsampler
        self.vsamper_label.setText(self.tr('计米轮:') + is_connect_title[faultDetectionPipeline.isVSamplerEnabled()])
        # length
        self.length_label.setText(
            self.tr('检测长度:') + '{:.2f}'.format(faultDetectionPipeline.accumulatedDistance()) + 'm')
        # time
        d, h, m, s = time_diff(self._startTime, datetime.now())
        self.run_time_label.setText(self.tr('运行时间:') + \
                                    str(d) + self.tr('天') + \
                                    str(h) + self.tr('时') + \
                                    str(m) + self.tr('分') + \
                                    str(s) + self.tr('秒'))
        now_time = datetime.now()
        self.time_label.setText(self.tr('当地时间:') + \
                                str(now_time.year) + self.tr('-') + \
                                str(now_time.month) + self.tr('-') + \
                                str(now_time.day) + self.tr(' ') + \
                                str(now_time.hour) + self.tr('-') +
                                str(now_time.minute) + self.tr('-') + \
                                str(now_time.second))
