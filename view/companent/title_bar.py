""" 设计稿标题栏: logo+系统名+版本 | 运行徽标 | 用户 | 告警铃 | 时钟 | 窗口按钮
子类化 qframelesswindow.TitleBar 保留拖拽与最小/最大/关闭按钮 """
import os
import time
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QLabel
from qframelesswindow import TitleBar

from .font import getFont
from core.const import Path
from core import faultDetectionPipeline
from core.signal_bus import SignalBus
from ..common import Theme
from ..session import Session


class AppTitleBar(TitleBar):
    def __init__(self, parent):
        super(AppTitleBar, self).__init__(parent)
        self.setFixedHeight(48)
        self._last_fault_t = 0.0
        self._alarm_count = 0

        # 窗口按钮深色主题可见
        for btn in (self.minBtn, self.maxBtn, self.closeBtn):
            btn.setFixedSize(46, 48)
            btn.setNormalColor(QColor(Theme.TXT))
            btn.setHoverColor(QColor('#FFFFFF'))
            btn.setPressedColor(QColor('#B9C0D0'))
            btn.setNormalBackgroundColor(QColor(0, 0, 0, 0))
            btn.setHoverBackgroundColor(QColor(255, 255, 255, 26))
            btn.setPressedBackgroundColor(QColor(255, 255, 255, 51))

        # ---- 左侧内容 ----
        self.hBoxLayout.insertSpacing(0, 12)
        self.logo = QSvgWidget(self)
        self.logo.load(os.path.join(Path.ICON, 'logo.svg'))
        self.logo.setFixedSize(26, 26)
        self.hBoxLayout.insertWidget(1, self.logo, 0, Qt.AlignVCenter)

        self.titleLabel = QLabel('漆包线表面缺陷检测系统', self)
        self.titleLabel.setFont(getFont(15, True))
        self.titleLabel.setStyleSheet(f'color:{Theme.TXT};background:transparent;padding:0 6px;')
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignVCenter)

        self.versionLabel = QLabel('V2.0', self)
        self.versionLabel.setFont(getFont(10))
        self.versionLabel.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        self.hBoxLayout.insertWidget(3, self.versionLabel, 0, Qt.AlignVCenter)

        # ---- 右侧内容(插在 stretch 之后, minBtn 之前) ----
        right = self.hBoxLayout.count() - 3  # min/max/close 占最后 3 位
        self.clockLabel = QLabel(self)
        self.clockLabel.setFont(getFont(12))
        self.clockLabel.setStyleSheet(f'color:{Theme.TXT2};background:transparent;padding:0 8px;')
        self.hBoxLayout.insertWidget(right, self.clockLabel, 0, Qt.AlignVCenter)

        self.bellLabel = QLabel('🔔 告警 0', self)
        self.bellLabel.setFont(getFont(12))
        self.bellLabel.setStyleSheet(
            f'color:{Theme.TXT};background:{Theme.CARD2};border:1px solid {Theme.BORDER};'
            f'border-radius:13px;padding:4px 12px;')
        self.hBoxLayout.insertWidget(right, self.bellLabel, 0, Qt.AlignVCenter)

        self.userLabel = QLabel('👤 未登录', self)
        self.userLabel.setFont(getFont(12))
        self.userLabel.setStyleSheet(
            f'color:{Theme.TXT};background:{Theme.CARD2};border:1px solid {Theme.BORDER};'
            f'border-radius:13px;padding:4px 12px;')
        self.hBoxLayout.insertWidget(right, self.userLabel, 0, Qt.AlignVCenter)

        self.runBadge = QLabel('已停止', self)
        self.runBadge.setFont(getFont(12, True))
        self.hBoxLayout.insertWidget(right, self.runBadge, 0, Qt.AlignVCenter)

        # ---- 刷新 ----
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(500)
        SignalBus.faultUpdated.connect(self._onFault)
        self._refresh()

    def setUserText(self, text: str):
        self.userLabel.setText(text)

    def _onFault(self):
        self._last_fault_t = time.time()
        self._alarm_count += 1
        self.bellLabel.setText(f'🔔 告警 {self._alarm_count}')
        self.bellLabel.setStyleSheet(
            f'color:{Theme.RED};background:#3A1A1C;border:1px solid {Theme.RED};'
            f'border-radius:13px;padding:4px 12px;')

    def _refresh(self):
        self.clockLabel.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if Session.user is None:
            self.userLabel.setText('👤 未登录')
        else:
            self.userLabel.setText(f'👤 {Session.username} · {Session.role.e2c()}')
        # 运行徽标
        alarming = (time.time() - self._last_fault_t) < 3
        if alarming:
            text, border, bg, fg = '⚠ 告警中', Theme.RED, '#3A1A1C', Theme.RED
        elif faultDetectionPipeline.isDetectEnabled():
            text, border, bg, fg = '● 运行中', Theme.GREEN, '#14351F', '#7BE49E'
        else:
            text, border, bg, fg = '已停止', '#5A6274', Theme.CARD2, Theme.TXT2
        self.runBadge.setText(text)
        self.runBadge.setStyleSheet(
            f'color:{fg};background:{bg};border:1px solid {border};border-radius:13px;padding:4px 14px;')
