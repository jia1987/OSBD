""" 设计稿弹窗: 登录 / 更换批次确认 / 告警(非模态自动关闭) """
import os
import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QCheckBox, QPushButton, QMessageBox, QWidget)

from .combox import UsersComboBox
from .font import getFont
from .label import Label
from .line_edit import LineEdit
from core.const import Path, Text
from core.database import UserManager
from core import faultDetectionPipeline
from ..common import Theme


class LoginDialog(QDialog):
    """ 启动登录弹窗 """

    def __init__(self, remembered: str = '', parent=None):
        super(LoginDialog, self).__init__(parent)
        self._user = None
        self._manager = UserManager()
        self.setWindowTitle('登录')
        self.setFixedWidth(420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(10)

        logo = QSvgWidget(self)
        logo.load(os.path.join(Path.ICON, 'logo.svg'))
        logo.setFixedSize(64, 64)
        layout.addWidget(logo, alignment=Qt.AlignHCenter)
        title = Label(text='漆包线表面缺陷检测系统', fontSize=17, weight=QFont.Bold)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        sub = Label(text='请登录以继续', fontSize=12)
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f'color:{Theme.TXT2};')
        layout.addWidget(sub)
        layout.addSpacing(12)

        layout.addWidget(Label(text='用户', fontSize=12))
        self.userBox = UsersComboBox(self)
        if remembered:
            idx = self.userBox.findText(remembered)
            if idx >= 0:
                self.userBox.setCurrentIndex(idx)
        layout.addWidget(self.userBox)
        layout.addWidget(Label(text='密码', fontSize=12))
        self.pwdEdit = QLineEdit(self)
        self.pwdEdit.setEchoMode(QLineEdit.Password)
        self.pwdEdit.setFixedHeight(38)
        layout.addWidget(self.pwdEdit)

        self.rememberBox = QCheckBox('记住我', self)
        layout.addWidget(self.rememberBox)
        layout.addSpacing(6)

        login_btn = QPushButton('登  录', self)
        login_btn.setFixedHeight(44)
        login_btn.setStyleSheet(
            f'QPushButton{{background:{Theme.ACCENT};color:#FFFFFF;border:none;border-radius:8px;font-size:15px;font-weight:bold;}}'
            f'QPushButton:hover{{background:#4AA8FF;}}'
            f'QPushButton:pressed{{background:#1F7ED6;}}')
        login_btn.clicked.connect(self._onLogin)
        layout.addWidget(login_btn)
        tip = Label(text='忘记密码请联系管理员', fontSize=11)
        tip.setAlignment(Qt.AlignCenter)
        tip.setStyleSheet(f'color:{Theme.TXT2};')
        layout.addWidget(tip)

        self.pwdEdit.returnPressed.connect(self._onLogin)

    def _onLogin(self):
        ok, data = self._manager.login(self.userBox.currentText(), self.pwdEdit.text())
        if not ok:
            QMessageBox.warning(self, '错误', data)
            return
        self._user = data
        self.accept()

    def user(self):
        return self._user

    def remember(self) -> bool:
        return self.rememberBox.isChecked()


class BatchSwitchDialog(QDialog):
    """ 更换批次确认弹窗: 输入新批次+负责人, 新旧对比展示; 空名拦截沿用原文案 """

    def __init__(self, parent=None):
        super(BatchSwitchDialog, self).__init__(parent)
        self.setWindowTitle('更换批次')
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addWidget(Label(text='更换批次确认', fontSize=15, weight=QFont.Bold))

        self.compareLabel = QLabel(self)
        self.compareLabel.setWordWrap(True)
        self.compareLabel.setStyleSheet(
            f'background:{Theme.CARD2};border:1px solid {Theme.BORDER};border-radius:6px;padding:10px;color:{Theme.TXT};')
        layout.addWidget(self.compareLabel)

        row1 = QHBoxLayout()
        row1.addWidget(Label(text='新批次:', fontSize=13))
        self.batchEdit = LineEdit(self)
        self.batchEdit.setPlaceholderText('输入批次名称')
        row1.addWidget(self.batchEdit, 1)
        layout.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(Label(text='负责人:', fontSize=13))
        self.workerBox = UsersComboBox(self)
        row2.addWidget(self.workerBox, 1)
        layout.addLayout(row2)

        warn = Label(text='⚠ 更换后, 缺陷计数与批次长度将重新累计, 缺陷保存至新批次目录', fontSize=11)
        warn.setStyleSheet(f'color:{Theme.YELLOW};')
        warn.setWordWrap(True)
        layout.addWidget(warn)

        btns = QHBoxLayout()
        cancel = QPushButton('取消', self)
        cancel.clicked.connect(self.reject)
        confirm = QPushButton('确认更换', self)
        confirm.setStyleSheet(
            f'QPushButton{{background:{Theme.ACCENT};color:#FFFFFF;border:none;border-radius:6px;padding:8px 20px;}}'
            f'QPushButton:hover{{background:#4AA8FF;}}')
        confirm.clicked.connect(self.accept)
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(confirm)
        layout.addLayout(btns)

        self.batchEdit.textChanged.connect(self._refresh_compare)
        self.workerBox.currentTextChanged.connect(lambda *_: self._refresh_compare())
        self._refresh_compare()

    def _refresh_compare(self):
        self.compareLabel.setText(
            f'当前批次: {faultDetectionPipeline.batchName() or ""}  ·  负责人: {faultDetectionPipeline.workerName() or ""}\n'
            f'新  批  次: {self.batchEdit.text()}  ·  负责人: {self.workerBox.currentText()}')

    def accept(self):
        # 空名拦截 (沿用历史文案)
        if self.batchEdit.text() == '':
            QMessageBox.warning(self.window(), '替换批次', '不接受空本作为批次名称')
            return
        super(BatchSwitchDialog, self).accept()

    def batchName(self) -> str:
        return self.batchEdit.text()

    def workerName(self) -> str:
        return self.workerBox.currentText()


class AlarmDialog(QWidget):
    """ 缺陷告警弹窗: 非模态/置顶/3 秒自动关闭 (UI_AlarmPopup 开启时使用) """

    def __init__(self, parent=None):
        super(AlarmDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(440)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._msg = QLabel(self)
        self._msg.setWordWrap(True)
        self._msg.setStyleSheet(
            f'background:{Theme.BG};border:2px solid {Theme.RED};border-radius:8px;'
            f'color:{Theme.TXT};padding:14px 18px;font-size:13px;')
        layout.addWidget(self._msg)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close)

    def showAlarm(self, text: str, timeout: int = 3000):
        self._msg.setText('⚠ 缺陷告警\n' + text)
        self.adjustSize()
        # 屏幕右下角
        screen = self.screen().geometry() if self.screen() else None
        if screen is not None:
            self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 60)
        self.show()
        self.raise_()
        self._timer.start(timeout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(Theme.BG))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)
