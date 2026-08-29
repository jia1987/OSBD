""" 系统设置-算法设置: YOLO/传统切换+置信度+预处理+通道启用与缺陷类型矩阵 """
import cpuinfo
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QSlider,
                             QCheckBox, QDoubleSpinBox, QSpinBox, QComboBox, QLabel)

from ...companent import Card, FormRow, Label, ToggleButton
from ...common import Theme
from core import faultDetectionPipeline
from core.config import config

FAULT_TYPES = ['汽包', '粒子', '漆瘤', '毛粘线']


class AlgorithmPage(QWidget):
    def __init__(self, parent=None):
        super(AlgorithmPage, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ---- 检测算法 ----
        card = Card('检测算法', self)
        c = card.contentLayout()
        row = QHBoxLayout()
        self.yoloRadio = QRadioButton('YOLO 深度学习检测 (推荐)', self)
        self.tradRadio = QRadioButton('传统算法 (FFT去纹理 + 梯度特征 + 轮廓分析)', self)
        self.yoloRadio.toggled.connect(self._on_algo_toggled)
        row.addWidget(self.yoloRadio)
        row.addWidget(self.tradRadio)
        row.addStretch(1)
        c.addLayout(row)
        conf_row = QHBoxLayout()
        conf_row.addWidget(Label(text='置信度阈值', fontSize=13))
        self.confSlider = QSlider(Qt.Horizontal, self)
        self.confSlider.setRange(5, 95)
        self.confSlider.setValue(int(config.get(config.Detect_Conf) * 100))
        self.confSlider.valueChanged.connect(self._on_conf)
        conf_row.addWidget(self.confSlider, 1)
        self.confLabel = Label(text=f'{config.get(config.Detect_Conf):.2f}', fontSize=14,
                               weight=QFont.Bold)
        self.confLabel.setStyleSheet(f'color:{Theme.ACCENT};background:transparent;')
        self.confLabel.setFixedWidth(50)
        conf_row.addWidget(self.confLabel)
        c.addLayout(conf_row)
        is_intel = 'Intel' in cpuinfo.get_cpu_info().get('brand_raw', '')
        engine = Label(text=f'当前模型: yolo_{"openvino_model" if is_intel else "onnx"} '
                            f'(4类: 汽包/粒子/漆瘤/毛粘线) · 阈值修改重启检测后生效', fontSize=11)
        engine.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        c.addWidget(engine)
        self.yoloRadio.setChecked(bool(config.get(config.Detect_UseYolo)))
        self.tradRadio.setChecked(not bool(config.get(config.Detect_UseYolo)))
        layout.addWidget(card)

        # ---- 预处理 ----
        card2 = Card('图像预处理', self)
        c2 = card2.contentLayout()
        r1 = FormRow('CLAHE 对比度限制')
        self.clipSpin = QDoubleSpinBox(self)
        self.clipSpin.setRange(0.5, 40)
        self.clipSpin.setValue(float(config.get(config.Prepare_ClipLimit)))
        self.clipSpin.valueChanged.connect(lambda v: config.set(config.Prepare_ClipLimit, v))
        r1.setWidget(self.clipSpin)
        c2.addWidget(r1)
        r2 = FormRow('CLAHE 分块大小')
        self.gridSpin = QSpinBox(self)
        self.gridSpin.setRange(2, 16)
        self.gridSpin.setValue(int(config.get(config.Prepare_Grid)))
        self.gridSpin.valueChanged.connect(lambda v: config.set(config.Prepare_Grid, v))
        r2.setWidget(self.gridSpin)
        c2.addWidget(r2)
        r3 = FormRow('检测 ROI 高度比例')
        self.roiCombo = QComboBox(self)
        self.roiCombo.addItems(['1/4', '1/3', '1/2'])
        ratios = {'1/4': 0.25, '1/3': 1 / 3, '1/2': 0.5}
        cur = float(config.get(config.Prepare_RoiRatio))
        self.roiCombo.setCurrentText(min(ratios, key=lambda k: abs(ratios[k] - cur)))
        self.roiCombo.currentTextChanged.connect(
            lambda t: config.set(config.Prepare_RoiRatio, ratios[t]))
        r3.setWidget(self.roiCombo)
        c2.addWidget(r3)
        tip = Label(text='预处理顺序: 透视矫正 → CLAHE 增强 → ROI 裁剪 → 送检', fontSize=11)
        tip.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        c2.addWidget(tip)
        layout.addWidget(card2)

        # ---- 通道启用与缺陷类型 ----
        card3 = Card('通道启用与缺陷类型 (型号配置, 内存中修改, 经"使用配置"落盘)', self)
        self._matrix_hint = QLabel(self)
        self._matrix_hint.setStyleSheet(f'color:{Theme.YELLOW};background:transparent;')
        card3.contentLayout().addWidget(self._matrix_hint)
        self._matrix_wrap = QVBoxLayout()
        card3.contentLayout().addLayout(self._matrix_wrap)
        layout.addWidget(card3)
        self._build_matrix()
        layout.addStretch(1)

    # ================= slots =================
    def _on_algo_toggled(self, on):
        config.set(config.Detect_UseYolo, bool(on))

    def _on_conf(self, v):
        self.confLabel.setText(f'{v / 100:.2f}')
        config.set(config.Detect_Conf, v / 100)

    # ================= 矩阵 =================
    def _build_matrix(self):
        # 清空重建
        while self._matrix_wrap.count():
            item = self._matrix_wrap.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        mc = faultDetectionPipeline.modelConfig()
        if mc is None:
            self._matrix_hint.setText('未选择型号配置: 请先在"型号管理"中选择/使用配置')
            return
        self._matrix_hint.setText('')
        for i, ctx in enumerate(faultDetectionPipeline.CHANNELS):
            row = QHBoxLayout()
            row.addWidget(Label(text=f'通道{i + 1}', fontSize=13, weight=QFont.Bold))
            toggle = ToggleButton(self)
            toggle.setChecked(bool(mc.enable.get(ctx, True)))
            toggle.toogled.connect(lambda on, ctx=ctx: self._set_enable(ctx, on))
            row.addWidget(toggle)
            row.addSpacing(12)
            allowed = (mc.typeFilter or {}).get(ctx)
            for ft in FAULT_TYPES:
                box = QCheckBox(ft, self)
                box.setChecked(allowed is None or ft in allowed)
                box.stateChanged.connect(lambda *_: self._collect_types(ctx))
                box.setProperty('ftype', ft)
                row.addWidget(box)
            row.addStretch(1)
            self._matrix_wrap.addLayout(row)

    def _set_enable(self, ctx, on):
        mc = faultDetectionPipeline.modelConfig()
        if mc is not None:
            mc.enable[ctx] = bool(on)

    def _collect_types(self, ctx):
        """ 收集该通道勾选的类型; 全勾选=不过滤(None) """
        mc = faultDetectionPipeline.modelConfig()
        if mc is None:
            return
        sender = self.sender()
        row_layout = None
        for i in range(self._matrix_wrap.count()):
            lay = self._matrix_wrap.itemAt(i).layout()
            if lay is not None and sender is not None and lay.indexOf(sender) >= 0:
                row_layout = lay
                break
        if row_layout is None:
            return
        checked = []
        for j in range(row_layout.count()):
            w = row_layout.itemAt(j).widget()
            if isinstance(w, QCheckBox) and w.isChecked():
                checked.append(w.property('ftype'))
        if mc.typeFilter is None:
            mc.typeFilter = {}
        mc.typeFilter[ctx] = checked if len(checked) < len(FAULT_TYPES) else None
        if all(v is None for v in mc.typeFilter.values()):
            mc.typeFilter = None
