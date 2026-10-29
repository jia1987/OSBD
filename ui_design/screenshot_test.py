# -*- coding: utf-8 -*-
""" UI 重构验收截图脚本 (在交互桌面运行):
    cd bin && ..\\env\\python.exe ui_design\\screenshot_test.py
    逐页抓取主窗口 + 关键弹窗, 输出到 ui_design/runtime/ 与设计稿比对 """
import os
import sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.getcwd())

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

OUT = os.path.join(os.getcwd(), 'ui_design', 'runtime')
os.makedirs(OUT, exist_ok=True)

app = QApplication(sys.argv)
import core.const  # 必须在 QApplication 之后

with open(os.path.join(core.const.Path.RC_DIR, 'qss', 'dark.qss'), encoding='utf-8') as f:
    app.setStyleSheet(f.read())

# 跳过登录: 直接以 admin 会话进入 (仅测试用途)
from view.session import Session
from core.database import UserManager, Role
Session.set_user({'id': 0, 'username': 'admin', 'role': Role.ADMIN})

from view import Window

w = Window()
w.resize(1920, 1080)
w.show()

from core import faultDetectionPipeline
faultDetectionPipeline.start()

STEPS = []


def snap(name):
    def do():
        p = os.path.join(OUT, f'{name}.png')
        w.grab().save(p)
        print('saved', p)
    return do


pages = [
    ('page_实时检测', w.detectionInterface),
    ('page_历史记录', w.memoryhInterface),
    ('page_设备设置', w.settingInterface),
    ('page_系统设置', w.systemInterface),
]
t = 1500
for name, page in pages:
    STEPS.append((t, lambda page=page: w.stackedWidget.setCurrentWidget(page)))
    STEPS.append((t + 800, snap(name)))
    t += 1600

# 弹窗截图
def shot_dialogs():
    from view.companent.dialogs import BatchSwitchDialog
    d = BatchSwitchDialog(w)
    d.show()
    # 抓弹窗自身 (grab 主窗口只会截到被遮罩的主界面)
    QTimer.singleShot(500, lambda: (d.grab().save(os.path.join(OUT, 'dialog_更换批次.png')), d.close()))


STEPS.append((t, shot_dialogs))
STEPS.append((t + 1500, lambda: (print('ALL DONE'), app.quit())))

for when, fn in STEPS:
    QTimer.singleShot(when, fn)
QTimer.singleShot(t + 10000, app.quit)  # 兜底

sys.exit(app.exec_())
