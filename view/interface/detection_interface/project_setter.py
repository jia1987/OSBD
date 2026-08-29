import functools
import json
import os.path
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QPushButton, QLineEdit, QSizePolicy
from PyQt5.QtWidgets import QSpacerItem, QGridLayout

from core import ModelConfig
from core import faultDetectionPipeline
from core.const import Path
from core.signal_bus import SignalBus
from ..system_interface.rectification_dialog import RectificationDialog
from ..._global import Function
from ...companent import Label, MaskBox, EdgegWidget, ComboBox, ToggleButton, PushButton, LineEdit, UsersComboBox

MODEL_CONFIG_PATH = os.path.join(Path.CONFIG_DIR, 'model')


class ModelComboBox(ComboBox):
    def showPopup(self):
        """ 动态加载Items """
        items = [i.removesuffix('.json') for i in os.listdir(MODEL_CONFIG_PATH) if i.endswith('.json')]
        self.setItems(items)
        super(ModelComboBox, self).showPopup()  # 弹出选项框


class PipelineCameraComboBox(ComboBox):
    def __init__(self, *args, **kwargs):
        super(PipelineCameraComboBox, self).__init__(*args, **kwargs)
        self._items = [f"相机{i + 1}" for i, _ in enumerate(faultDetectionPipeline.CAMERA_LIST)]
        self.addItems(self._items)


class ExposureBatchBox(ComboBox):
    def __init__(self, *args, **kwargs):
        super(ExposureBatchBox, self).__init__(*args, **kwargs)
        self._items = [f"批次:{i + 1}" for i, _ in enumerate(faultDetectionPipeline.CAMERA_LIST)]
        self.addItems(self._items)


class BatchNameWidget(EdgegWidget):
    PREX_NOW = '当前'
    PREX_BATCH = '批次:'
    PREX_WORKER = '负责人:'

    def __init__(self, parent=None):
        super(BatchNameWidget, self).__init__(parent)
        self.batch_name_label = Label(text=self.PREX_NOW + self.PREX_BATCH, fontSize=16, parent=self)
        self.woker_label = Label(text=self.PREX_NOW + self.PREX_WORKER, fontSize=16, parent=self)
        self.batch_name_edit = LineEdit(parent=self)
        self.swap_batch_btn = PushButton(text=self.tr('更换\n批次'), parent=self)
        self.usersBox = UsersComboBox(self)

        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(5, 5, 5, 5)
        self.hlayout1 = QHBoxLayout()
        self.hlayout2 = QHBoxLayout()
        self.glayout1 = QGridLayout()
        self.viewLayout.addWidget(self.batch_name_label)
        self.viewLayout.addWidget(self.woker_label)
        # layout: 2
        self.glayout1.addWidget(Label(self.tr(self.PREX_BATCH), fontSize=16, parent=self), 0, 0,
                                alignment=Qt.AlignRight)
        self.glayout1.addWidget(self.batch_name_edit, 0, 1)
        self.glayout1.addWidget(Label(self.tr(self.PREX_WORKER), fontSize=16, parent=self), 1, 0,
                                alignment=Qt.AlignRight)
        self.glayout1.addWidget(self.usersBox, 1, 1)
        self.hlayout2.addLayout(self.glayout1)
        self.hlayout2.addWidget(self.swap_batch_btn)
        self.viewLayout.addLayout(self.hlayout2)

        self.swap_batch_btn.clicked.connect(self._batch_name_clicked)
        SignalBus.batchUpdated.connect(
            lambda b, w: (self.batch_name_label.setText(self.tr(self.PREX_NOW + self.PREX_BATCH) + b),
                          self.woker_label.setText(self.tr(self.PREX_NOW + self.PREX_WORKER) + w),))

    def _batch_name_clicked(self, ):
        if self.batch_name_edit.text() == '':
            QMessageBox.warning(self.window(),
                                '替换批次',
                                f"不接受空本作为批次名称")
            return
        reply = QMessageBox.question(self.window(),
                                     '替换批次',
                                     f"{self.PREX_BATCH}{faultDetectionPipeline.batchName() or ''} -> {self.batch_name_edit.text()}\n"
                                     f"{self.PREX_WORKER}{faultDetectionPipeline.workerName() or ''} -> {self.usersBox.currentText()}\n"
                                     f"替换后,新的缺陷信息将记录到新批次",
                                     QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No), )
        if reply == QMessageBox.Yes:
            Function.swapBatch(batchName=self.batch_name_edit.text(), wokerName=self.usersBox.currentText())
            self.batch_name_edit.clear()


class ModelCameraSettingWidget(QWidget):
    """ 对摄像头在系统和在物理装置对应的设置 """
    configChanged = pyqtSignal()  # 通知外部组件, config发生了变更

    def __init__(self, parent=None):
        self._model_config: ModelConfig = None
        self._syncing = False
        super(ModelCameraSettingWidget, self).__init__(parent)
        self.viewlayout = QGridLayout(self)
        self.viewlayout.setContentsMargins(0, 0, 0, 0)
        self.viewlayout.addWidget(Label(text=self.tr('摄像头')), 0, 1, alignment=Qt.AlignCenter)
        self.viewlayout.addWidget(Label(text=self.tr('曝光批次')), 0, 2, alignment=Qt.AlignCenter)
        self.viewlayout.addWidget(Label(text=self.tr('使能')), 0, 3, alignment=Qt.AlignCenter)
        self.cameraComboxs: List[PipelineCameraComboBox] = []
        self.exposureBatchComboxs: List[ExposureBatchBox] = []
        self.btns: List[ToggleButton] = []
        for i, c in enumerate(faultDetectionPipeline.CHANNELS):
            combox1 = PipelineCameraComboBox()
            combox2 = ExposureBatchBox()
            btn = ToggleButton()
            self.viewlayout.addWidget(Label(self.tr('管线') + str(i + 1)), i + 1, 0, )
            self.viewlayout.addWidget(combox1, i + 1, 1)
            self.viewlayout.addWidget(combox2, i + 1, 2)
            self.viewlayout.addWidget(btn, i + 1, 3)
            combox1.currentTextChanged.connect(functools.partial(self._on_combox1_currentTextChanged, c, combox1))
            combox2.currentTextChanged.connect(
                functools.partial(self._on_combox2_currentTextChanged, c, combox1, combox2))
            btn.clicked.connect(functools.partial(self._on_btn_clicked, c, btn))
            self.cameraComboxs.append(combox1)
            self.btns.append(btn)
            self.exposureBatchComboxs.append(combox2)
        self.viewlayout.setColumnStretch(0, 0)
        self.viewlayout.setColumnStretch(1, 1)
        self.viewlayout.setColumnStretch(2, 1)

    def _on_combox1_currentTextChanged(self, ctx, combox: PipelineCameraComboBox):
        if self._model_config is None: return
        self._model_config.mapper[ctx] = faultDetectionPipeline.CAMERA_LIST[combox.currentIndex()]
        self._update_from_config()
        self.configChanged.emit()

    def _on_combox2_currentTextChanged(self, ctx, cc: PipelineCameraComboBox, ec: ExposureBatchBox):
        if self._model_config is None: return
        self._model_config.exposureBatch[faultDetectionPipeline.CAMERA_LIST[cc.currentIndex()]] = ec.currentIndex()
        self._update_from_config()
        self.configChanged.emit()

    def _on_btn_clicked(self, ctx, btn: ToggleButton):
        if self._model_config is None: return
        self._model_config.enable[ctx] = btn.isChecked()
        self._update_from_config()
        self.configChanged.emit()

    def setModelConfig(self, config: ModelConfig):
        """ setter """
        self._model_config = config
        self._update_from_config()

    def _update_from_config(self):
        if self._syncing:
            return
        self._syncing = True
        # 同步
        for c, cc, ec, btn in zip(faultDetectionPipeline.CHANNELS, self.cameraComboxs, self.exposureBatchComboxs,
                                  self.btns):
            cc.setCurrentIndex(faultDetectionPipeline.CAMERA_LIST.index(self._model_config.mapper[c]))
            ec.setCurrentIndex(self._model_config.exposureBatch[faultDetectionPipeline.CAMERA_LIST[cc.currentIndex()]])

            btn.setChecked(self._model_config.enable[c])
        self._syncing = False


class ModelSettingWidget(EdgegWidget):
    def __init__(self, parent=None):
        self._model_config: ModelConfig = None
        super(ModelSettingWidget, self).__init__(parent)

        self.initWidget()
        self.initConnect()
        self.initLayout()

    def initWidget(self):
        # model configuation
        self.now_model_label = Label(text=self.tr('当前配置:'), fontSize=18, parent=self)
        self.model_combo_box = ModelComboBox(parent=self)
        self.add_model_btn = PushButton(text=self.tr('添加型号'), parent=self)
        self.set_model_btn = PushButton(text=self.tr('使用配置'), parent=self)
        self.save_model_btn = PushButton(text=self.tr('保存配置'), parent=self)
        self.set_affineTransform_btn = PushButton(text='放射变换', parent=self)
        self.set_camera_mapper = ModelCameraSettingWidget(parent=self)

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(5, 5, 5, 5)
        self.hlayout1 = QHBoxLayout()
        self.hlayout2 = QHBoxLayout()
        self.hlayout3 = QHBoxLayout()

        # layout: 2
        self.viewLayout.addWidget(self.now_model_label)
        self.hlayout2.addWidget(self.model_combo_box)
        self.hlayout2.addWidget(self.add_model_btn)
        self.viewLayout.addLayout(self.hlayout2)
        self.viewLayout.addWidget(self.set_affineTransform_btn)

        self.hlayout3.addWidget(self.set_model_btn)
        self.hlayout3.addWidget(self.save_model_btn)
        self.viewLayout.addWidget(self.set_camera_mapper)
        self.viewLayout.addLayout(self.hlayout3)

        self.viewLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

    def initConnect(self):
        self.add_model_btn.clicked.connect(self._on_add_model_btn_clicked)
        self.model_combo_box.currentTextChanged.connect(self._open_model_config)
        self.set_affineTransform_btn.clicked.connect(self._on_set_affineTransform_btn_clecked)
        self.save_model_btn.clicked.connect(self._save_model_config)
        self.set_model_btn.clicked.connect(self._on_set_model_btn_clicked)

    def _on_add_model_btn_clicked(self):
        """ 添加新的型号配置"""
        string, success = QInputDialog.getText(self.window(), self.tr('创建型号配置'), self.tr('输入型号'))
        # 是否取消
        if not success:
            return

        # 是否已经存在
        config = os.path.join(MODEL_CONFIG_PATH, f'{string}.json')
        if os.path.exists(config):
            QMessageBox.warning(self, "创建型号配置", f"{string}已被占用", QMessageBox.Ok)
            return

        # 创建
        if not os.path.exists(os.path.dirname(config)):
            os.makedirs(os.path.dirname(config))
        with open(config, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4, ensure_ascii=False)

    def _open_model_config(self):
        """ 打开一个型号配置 """
        path = os.path.join(MODEL_CONFIG_PATH, f'{self.model_combo_box.currentText()}.json')
        self._model_config = ModelConfig.load(path)
        # 同步到子组件
        self.set_camera_mapper.setModelConfig(self._model_config)

    def _save_model_config(self):
        """ 保存一个型号配置 """
        if self._model_config is None: return
        path = os.path.join(MODEL_CONFIG_PATH, f'{self.model_combo_box.currentText()}.json')
        self._model_config.save(path)

    def _on_set_model_btn_clicked(self):
        """ 设置 型号配置 运用到管线中"""
        if self._model_config is None:
            return
        reply = QMessageBox.question(self.window(),
                                     '设置型号配置',
                                     f"新的型号配置将会被保存，以及用于检测管线，请确保所有配置已经设置",
                                     QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No), )
        if reply == QMessageBox.Yes:
            path = os.path.join(MODEL_CONFIG_PATH, f'{self.model_combo_box.currentText()}.json')
            self._model_config.save(path)
            faultDetectionPipeline.setModelConfig(path)
            self.now_model_label.setText(self.tr('当前配置:') + ' ' + self.model_combo_box.currentText())

    def _on_set_affineTransform_btn_clecked(self):
        """ 点击事件: 打开升级版透视矫正弹窗 (画布拖拽4端点, 仅改内存) """
        if self._model_config is None: return
        RectificationDialog(self._model_config, self.window()).exec_()


class BatchSettingWidget(EdgegWidget):
    def __init__(self, parent):
        super(BatchSettingWidget, self).__init__(parent)

        self.batchNameWidget = BatchNameWidget(parent=self)
        self.modelSettingWidget = ModelSettingWidget(parent=self)
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(5, 5, 5, 5)
        self.viewLayout.addWidget(self.batchNameWidget)
        self.viewLayout.addWidget(self.modelSettingWidget)

        self.setMinimumWidth(256)
