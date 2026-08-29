""" 曝光批次分组编辑: 4 路相机各选批次1-4 (键=物理相机名), 仅改内存 ModelConfig
落盘沿用"保存配置/使用配置" """
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton

from .label import Label
from core.pipeline.meta import PipelineType


class GroupEditorDialog(QDialog):
    def __init__(self, model_config, parent=None):
        super(GroupEditorDialog, self).__init__(parent)
        self._mc = model_config
        self.setWindowTitle('曝光批次分组')
        self.setFixedWidth(380)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.addWidget(Label(text='同组相机同时频闪 (相同批次号)', fontSize=12))
        self._combos = {}
        for cam in PipelineType.CAMERA_LIST:
            row = QHBoxLayout()
            row.addWidget(Label(text=f'{cam}:', fontSize=13))
            combo = QComboBox(self)
            combo.addItems(['批次:1', '批次:2', '批次:3', '批次:4'])
            combo.setCurrentIndex(int(self._mc.exposureBatch.get(cam, 0)))
            self._combos[cam] = combo
            row.addWidget(combo, 1)
            layout.addLayout(row)
        btns = QHBoxLayout()
        cancel = QPushButton('取消', self)
        cancel.clicked.connect(self.reject)
        ok = QPushButton('确定', self)
        ok.clicked.connect(self.accept)
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)

    def accept(self):
        for cam, combo in self._combos.items():
            self._mc.exposureBatch[cam] = combo.currentIndex()
        super(GroupEditorDialog, self).accept()
