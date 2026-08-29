""" 系统设置-型号管理: 复用 ModelSettingWidget + 型号复制/删除 """
import os
import shutil

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QInputDialog)

from ...companent import PushButton
from core.const import Path

MODEL_DIR = os.path.join(Path.CONFIG_DIR, 'model')


class ModelPage(QWidget):
    def __init__(self, parent=None):
        super(ModelPage, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        btns = QHBoxLayout()
        copy_btn = PushButton(self, text='复制型号')
        copy_btn.clicked.connect(self._copy_model)
        del_btn = PushButton(self, text='删除型号')
        del_btn.clicked.connect(self._delete_model)
        btns.addStretch(1)
        btns.addWidget(copy_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

        from ..detection_interface.project_setter import ModelSettingWidget
        self.setting = ModelSettingWidget(parent=self)
        layout.addWidget(self.setting, 1)

    def _current_name(self):
        return self.setting.model_combo_box.currentText()

    def _copy_model(self):
        name = self._current_name()
        if not name:
            return
        new_name, ok = QInputDialog.getText(self.window(), '复制型号', '新型号名称')
        if not ok or not new_name:
            return
        src = os.path.join(MODEL_DIR, f'{name}.json')
        dst = os.path.join(MODEL_DIR, f'{new_name}.json')
        if os.path.exists(dst):
            QMessageBox.warning(self.window(), '复制型号', f'{new_name}已被占用')
            return
        shutil.copyfile(src, dst)
        self.setting.model_combo_box.setCurrentText(new_name)

    def _delete_model(self):
        name = self._current_name()
        if not name:
            return
        if QMessageBox.question(self.window(), '删除型号', f'确认删除型号 {name} ?',
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        try:
            os.remove(os.path.join(MODEL_DIR, f'{name}.json'))
        except OSError as e:
            QMessageBox.warning(self.window(), '删除型号', str(e))
