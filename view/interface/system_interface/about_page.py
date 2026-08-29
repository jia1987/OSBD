""" 系统设置-关于: 版本/机器码/授权状态 """
import os

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from ...companent import Card, Label
from ...common import Theme
from core.const import Text
from core.utils.machine_id import get_machine_fingerprint, verify_license


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super(AboutPage, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        card = Card('关于系统', self)
        c = card.contentLayout()
        t = Label(text='漆包线表面缺陷检测系统 V2.0', fontSize=16, weight=QFont.Bold)
        t.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        c.addWidget(t)
        mid = get_machine_fingerprint(extra_salt=Text.APP_NAME)
        pub = os.path.join('config', 'pub_key')
        lic = os.path.join('config', 'license')
        if os.path.exists(pub) and os.path.exists(lic):
            with open(pub, 'rb') as f:
                pub_b = f.read()
            with open(lic, 'r') as f:
                lic_s = f.read()
            ok, msg = verify_license(pub_b, lic_s, extra_salt=Text.APP_NAME)
            auth = '已激活' if ok else f'授权异常: {msg}'
        else:
            auth = '未部署授权文件 (开发/验收环境)'
        for text in (f'机器码: {mid}', f'授权状态: {auth}',
                     '检测引擎: YOLO (OpenVINO/ONNX) + 传统算法后备',
                     '硬件: 海康工业相机×4 · 光源控制器 · 计米轮 · 放电检测 · IO 卡'):
            lab = Label(text=text, fontSize=12)
            lab.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
            c.addWidget(lab)
        layout.addWidget(card)
        layout.addStretch(1)
