""" 系统设置页 (设计稿 P6): 子导航 算法设置/透视矫正/型号管理/用户管理/关于系统 """
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
                             QPushButton)

from ...companent import Card
from ...common import Theme
from ...session import Session
from core import faultDetectionPipeline
from .about_page import AboutPage
from .algorithm_page import AlgorithmPage
from .model_page import ModelPage
from .rectification_dialog import RectificationDialog
from .users_page import UsersPage


class SystemInterface(QWidget):
    def __init__(self, parent=None):
        super(SystemInterface, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ---- 子导航 ----
        nav = QListWidget(self)
        nav.setFixedWidth(190)
        nav.addItems(['算法设置', '透视矫正', '型号管理', '用户管理', '关于系统'])
        if not Session.is_admin:
            # 用户管理仅管理员可见
            nav.item(3).setHidden(True)
        layout.addWidget(nav)

        self._stack = QStackedWidget(self)
        self._algo = AlgorithmPage(self)
        self._rect_card = self._build_rect_entry()
        self._model = ModelPage(self)
        self._users = UsersPage(self)
        self._about = AboutPage(self)
        self._stack.addWidget(self._algo)
        self._stack.addWidget(self._rect_card)
        self._stack.addWidget(self._model)
        self._stack.addWidget(self._users)
        self._stack.addWidget(self._about)
        layout.addWidget(self._stack, 1)

        nav.currentRowChanged.connect(self._stack.setCurrentIndex)

    def _build_rect_entry(self):
        card = Card('透视矫正 (仿射变换)', self)
        c = card.contentLayout()
        tip = Label(text='每通道 4 参数: top_lower / top_upper / bottom_lower / bottom_upper;\n'
                         '在实时画面上拖拽端点, 将梯形漆包线区域矫正为矩形', fontSize=12)
        tip.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        c.addWidget(tip)
        btn = QPushButton('打开矫正工具', self)
        btn.setFixedWidth(180)
        btn.setStyleSheet(
            f'background:{Theme.ACCENT};color:#FFFFFF;border:none;border-radius:6px;'
            f'padding:9px 0;font-weight:bold;')
        btn.clicked.connect(self._open_rect)
        c.addWidget(btn)
        c.addStretch(1)
        return card

    def _open_rect(self):
        mc = faultDetectionPipeline.modelConfig()
        if mc is None:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self.window(), '透视矫正', '请先在"型号管理"中选择型号配置')
            return
        RectificationDialog(mc, self.window()).exec_()
