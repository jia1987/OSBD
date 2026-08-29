""" 设备设置页 (设计稿 P5): 相机大表 + 光源/计米轮/放电/IO卡 卡片
所有串口/相机参数即时写 config (沿用历史行为); 型号相关(启用/曝光组)仅改内存 """
import threading

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
                             QSlider, QSpinBox, QDoubleSpinBox, QLabel, QMessageBox, QScrollArea)

from ...companent import (Card, FormRow, Label, PushButton, StatusChip, ToggleButton,
                          SerialPortComboBox, FileLoadBox, SpinBox, DoubleSpinBox)
from ...companent.group_editor import GroupEditorDialog
from ...companent.preview_dialog import PreviewDialog
from ...common import Theme
from core import faultDetectionPipeline
from core.config import config
from core.pipeline.device.camera import Camera, HK_Camera

READ_MODES = ['海康威视', '摄像头', '视频', '图片']
MODE_KEYS = [Camera.ReadMode_Hk, Camera.ReadMode_Capture, Camera.ReadMode_Vedio, Camera.ReadMode_Img]


def set_list(item, idx, value):
    """ 列表型配置项: 取整表→改[idx]→写回 (沿用历史 set 模式, 即时落盘) """
    lst = list(config.get(item))
    lst[idx] = value
    config.set(item, lst)


class _IOLights(QWidget):
    """ 8 路输入指示灯 """

    def __init__(self, reader, parent=None):
        super(_IOLights, self).__init__(parent)
        self._reader = reader
        self.setFixedHeight(20)
        self.setMinimumWidth(8 * 24)

    def paintEvent(self, event):
        painter = QPainter(self)
        vals = self._reader() or [0] * 8
        for i in range(8):
            on = bool(vals[i]) if i < len(vals) else False
            painter.setPen(QPen(QColor(Theme.BORDER), 1))
            painter.setBrush(QColor(Theme.RED if on else '#3A4152'))
            painter.drawEllipse(i * 24, 2, 16, 16)


class CameraRow(QWidget):
    def __init__(self, idx: int, parent=None):
        super(CameraRow, self).__init__(parent)
        self._idx = idx
        self._syncing = False
        layout = QGridLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        layout.addWidget(Label(text=f'通道{idx + 1}', fontSize=13, weight=QFont.Bold), 0, 0)

        self.modeCombo = QComboBox(self)
        self.modeCombo.addItems(READ_MODES)
        self.modeCombo.currentIndexChanged.connect(self._on_mode_changed)
        layout.addWidget(self.modeCombo, 0, 1)

        # 设备源 (按模式切换)
        self.hkCombo = QComboBox(self)
        self.hkCombo.currentTextChanged.connect(self._on_hk_changed)
        self.captureSpin = SpinBox(self)
        self.captureSpin.setRange(0, 16)
        self.captureSpin.valueChanged.connect(lambda v: set_list(config.Camera_Captures, idx, v))
        self.videoBox = FileLoadBox(self, filter='Video Files (*.mp4 *.avi *.mov *.mkv)', title='选择视频')
        self.videoBox.pathChanged.connect(lambda p: p and set_list(config.Camera_Videos, idx, p))
        self.imgBox = FileLoadBox(self, filter='Images (*.png *.jpg *.jpeg)', title='选择图片')
        self.imgBox.pathChanged.connect(lambda p: p and set_list(config.Camera_Imgs, idx, p))
        self._src_wrap = QVBoxLayout()
        self._src_wrap.setContentsMargins(0, 0, 0, 0)
        for w in (self.hkCombo, self.captureSpin, self.videoBox, self.imgBox):
            self._src_wrap.addWidget(w)
        layout.addLayout(self._src_wrap, 0, 2)

        self.exposureSpin = SpinBox(self)
        self.exposureSpin.setRange(0, 65536)
        self.exposureSpin.valueChanged.connect(lambda v: set_list(config.Camera_Exposures, idx, v))
        layout.addWidget(self.exposureSpin, 0, 3)

        self.triggerCombo = QComboBox(self)
        self.triggerCombo.addItems(['频闪', '连续'])
        self.triggerCombo.currentIndexChanged.connect(self._on_trigger_changed)
        layout.addWidget(self.triggerCombo, 0, 4)

        self.stateChip = StatusChip('未连接', 'err', self)
        layout.addWidget(self.stateChip, 0, 5)

        self.enableToggle = ToggleButton(self)
        self.enableToggle.toogled.connect(self._on_enable_toggled)
        layout.addWidget(self.enableToggle, 0, 6)

        prev = PushButton(self, text='预览')
        prev.setFixedSize(52, 26)
        prev.clicked.connect(lambda: PreviewDialog(idx, self.window()).show())
        layout.addWidget(prev, 0, 7)

        self._load_from_config()

    def _load_from_config(self):
        self._syncing = True
        mode = config.get(config.Camera_ReadModes)[self._idx]
        mi = MODE_KEYS.index(mode) if mode in MODE_KEYS else 0
        self.modeCombo.setCurrentIndex(mi)
        self._show_source(mi)
        self.hkCombo.clear()
        self.hkCombo.addItems(['None'])
        cur = config.get(config.Camera_Prots)[self._idx]
        if cur and cur != 'None':
            self.hkCombo.addItem(cur)
            self.hkCombo.setCurrentText(cur)
        self.captureSpin.setValue(int(config.get(config.Camera_Captures)[self._idx]))
        self.videoBox.setPath(config.get(config.Camera_Videos)[self._idx] or '')
        self.imgBox.setPath(config.get(config.Camera_Imgs)[self._idx] or '')
        self.exposureSpin.setValue(int(config.get(config.Camera_Exposures)[self._idx]))
        trig = config.get(config.Camera_Triggers)[self._idx]
        self.triggerCombo.setCurrentIndex(0 if trig else 1)
        # 启用 (型号配置, 仅内存)
        mc = faultDetectionPipeline.modelConfig()
        if mc is not None:
            self.enableToggle.setChecked(bool(mc.enable.get(f'c{self._idx + 1}', True)))
        else:
            self.enableToggle.setEnabled(False)
        self._syncing = False

    def _show_source(self, mi):
        for i, w in enumerate((self.hkCombo, self.captureSpin, self.videoBox, self.imgBox)):
            w.setVisible(i == mi)

    def refresh_hk_devices(self):
        """ 弹出时动态加载海康设备列表 """
        cur = self.hkCombo.currentText()
        self.hkCombo.clear()
        self.hkCombo.addItems(['None'] + list(HK_Camera.device_list()))
        if cur:
            self.hkCombo.setCurrentText(cur)

    # ---------------- slots ----------------
    def _on_mode_changed(self, mi):
        if self._syncing:
            return
        set_list(config.Camera_ReadModes, self._idx, MODE_KEYS[mi])
        self._show_source(mi)

    def _on_hk_changed(self, text):
        if self._syncing or not text:
            return
        set_list(config.Camera_Prots, self._idx, text)

    def _on_trigger_changed(self, ti):
        if self._syncing:
            return
        set_list(config.Camera_Triggers, self._idx, ti == 0)

    def _on_enable_toggled(self, on):
        mc = faultDetectionPipeline.modelConfig()
        if mc is None:
            return
        mc.enable[f'c{self._idx + 1}'] = bool(on)

    def refresh_state(self):
        info = faultDetectionPipeline.channels(ctx=f'c{self._idx + 1}')
        online = info is not None and info.camera is not None
        self.stateChip.setText('已连接' if online else '未连接')
        self.stateChip.setState('ok' if online else 'err')


class DeviceSettingPage(QWidget):
    def __init__(self, parent=None):
        super(DeviceSettingPage, self).__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)

        head = QHBoxLayout()
        t = Label(text='设备设置', fontSize=18, weight=QFont.Bold)
        t.setStyleSheet(f'color:{Theme.TXT};background:transparent;')
        head.addWidget(t)
        head.addWidget(Label(text='硬件连接与参数配置 · 修改即时保存', fontSize=12))
        head.addStretch(1)
        restore = PushButton(self, text='恢复默认')
        restore.clicked.connect(self._restore_defaults)
        head.addWidget(restore)
        outer.addLayout(head)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        content = QWidget()
        grid = QVBoxLayout(content)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)

        grid.addWidget(self._build_camera_card())
        row1 = QHBoxLayout()
        row1.addWidget(self._build_light_card(), 1)
        row1.addWidget(self._build_vsampler_card(), 1)
        grid.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(self._build_lightning_card(), 1)
        row2.addWidget(self._build_iocard_card(), 1)
        grid.addLayout(row2)
        grid.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1000)
        self._refresh()

    # ================= 相机大卡 =================
    def _build_camera_card(self):
        card = Card('相机设置 (4 路检测通道)', self)
        hdr = QHBoxLayout()
        for text, w in [('通道', 60), ('读取模式', 110), ('设备 / 信号源', 260),
                        ('曝光(µs)', 90), ('触发', 70), ('状态', 90), ('启用', 60), ('操作', 60)]:
            lab = Label(text=text, fontSize=12, weight=QFont.Bold)
            lab.setFixedWidth(w)
            lab.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
            hdr.addWidget(lab)
        hdr.addStretch(1)
        card.contentLayout().addLayout(hdr)
        self._camera_rows = []
        for i in range(4):
            row = CameraRow(i, self)
            self._camera_rows.append(row)
            card.contentLayout().addWidget(row)
        tip = Label(text='支持模式: 海康威视(生产) / USB摄像头 / 视频文件(演示) / 静态图片(调试); '
                         '启用开关与曝光分组属于型号配置, 需在"型号/批次管理"中保存', fontSize=11)
        tip.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        card.contentLayout().addWidget(tip)
        return card

    # ================= 光源 =================
    def _build_light_card(self):
        card = Card('光源控制器', self)
        self.light_chip = StatusChip('未启用', 'off')
        card.headerExtraLayout().addWidget(self.light_chip)
        card.headerExtraLayout().addStretch(1)
        c = card.contentLayout()
        r1 = FormRow('串口端口')
        self.light_port = SerialPortComboBox(self)
        self.light_port.currentTextChanged.connect(
            lambda t: t and config.set(config.LightSource_Port, t))
        self.light_port.setCurrentText(config.get(config.LightSource_Port) or 'None')
        r1.setWidget(self.light_port)
        c.addWidget(r1)
        r2 = FormRow('波特率')
        self.light_baud = SpinBox(self)
        self.light_baud.setRange(0, 2 ** 31 - 1)
        self.light_baud.setValue(int(config.get(config.LightSource_Baudrate)))
        self.light_baud.valueChanged.connect(lambda v: config.set(config.LightSource_Baudrate, v))
        r2.setWidget(self.light_baud)
        c.addWidget(r2)
        self._light_sliders = []
        levels = config.get(config.LightSource_Levels)
        for i in range(4):
            row = QHBoxLayout()
            row.addWidget(Label(text=f'通道{chr(65 + i)}', fontSize=12))
            slider = QSlider(self)
            slider.setOrientation(Qt.Horizontal)
            slider.setRange(0, 255)
            slider.setValue(int(levels[i]))
            val = Label(text=str(levels[i]), fontSize=12)
            val.setFixedWidth(36)

            def on_change(v, i=i, val=val):
                val.setText(str(v))
                lst = list(config.get(config.LightSource_Levels))
                lst[i] = v
                config.set(config.LightSource_Levels, lst)
                faultDetectionPipeline.setLightLevels(lst)

            slider.valueChanged.connect(on_change)
            self._light_sliders.append(slider)
            row.addWidget(slider, 1)
            row.addWidget(val)
            c.addLayout(row)
        grp = QHBoxLayout()
        grp.addWidget(Label(text='曝光分组:', fontSize=12))
        self._group_label = QLabel()
        self._group_label.setStyleSheet(f'color:{Theme.TEAL};background:transparent;')
        grp.addWidget(self._group_label, 1)
        edit_grp = PushButton(self, text='编辑分组')
        edit_grp.setFixedSize(80, 26)
        edit_grp.clicked.connect(self._edit_group)
        grp.addWidget(edit_grp)
        c.addLayout(grp)
        return card

    def _edit_group(self):
        mc = faultDetectionPipeline.modelConfig()
        if mc is None:
            QMessageBox.warning(self.window(), '编辑分组', '请先在"型号/批次管理"中选择型号配置')
            return
        dlg = GroupEditorDialog(mc, self.window())
        if dlg.exec_():
            self._refresh()

    # ================= 计米轮 =================
    def _build_vsampler_card(self):
        card = Card('计米轮 (测速编码器)', self)
        self.vsam_chip = StatusChip('未启用', 'off')
        card.headerExtraLayout().addWidget(self.vsam_chip)
        card.headerExtraLayout().addStretch(1)
        c = card.contentLayout()
        r1 = FormRow('串口端口')
        self.vsam_port = SerialPortComboBox(self)
        self.vsam_port.currentTextChanged.connect(lambda t: t and config.set(config.VSampler_Port, t))
        self.vsam_port.setCurrentText(config.get(config.VSampler_Port) or 'None')
        r1.setWidget(self.vsam_port)
        c.addWidget(r1)
        r2 = FormRow('波特率')
        self.vsam_baud = SpinBox(self)
        self.vsam_baud.setRange(0, 2 ** 31 - 1)
        self.vsam_baud.setValue(int(config.get(config.VSampler_Baudrate)))
        self.vsam_baud.valueChanged.connect(lambda v: config.set(config.VSampler_Baudrate, v))
        r2.setWidget(self.vsam_baud)
        c.addWidget(r2)
        r3 = FormRow('单圈周长 (cm)')
        self.vsam_peri = DoubleSpinBox(self)
        self.vsam_peri.setRange(0.01, 10000)
        self.vsam_peri.setDecimals(2)
        self.vsam_peri.setValue(float(config.get(config.VSampler_Perimeter)) * 100)
        self.vsam_peri.valueChanged.connect(
            lambda v: config.set(config.VSampler_Perimeter, v / 100))
        r3.setWidget(self.vsam_peri)
        c.addWidget(r3)
        r4 = FormRow('计数方向')
        self.vsam_dir = ToggleButton(self)
        self.vsam_dir.setChecked(bool(config.get(config.VSampler_Direction)))
        self.vsam_dir.toogled.connect(lambda on: config.set(config.VSampler_Direction, on))
        r4.setWidget(self.vsam_dir)
        r4.addWidget(Label(text='反向', fontSize=12))
        c.addWidget(r4)
        self.vsam_info = QLabel()
        self.vsam_info.setStyleSheet(f'color:{Theme.TEAL};background:transparent;')
        c.addWidget(self.vsam_info)
        btns = QHBoxLayout()
        zero = PushButton(self, text='累计清零')
        zero.clicked.connect(lambda: faultDetectionPipeline.resetDistance())
        test = PushButton(self, text='读取测试')
        test.clicked.connect(lambda: QMessageBox.information(
            self.window(), '读取测试', f'当前速度: {faultDetectionPipeline.velocity():.3f} m/s'))
        btns.addStretch(1)
        btns.addWidget(zero)
        btns.addWidget(test)
        c.addLayout(btns)
        return card

    # ================= 放电 =================
    def _build_lightning_card(self):
        card = Card('放电检测 (针孔)', self)
        self.lightning_chip = StatusChip('未启用', 'off')
        card.headerExtraLayout().addWidget(self.lightning_chip)
        card.headerExtraLayout().addStretch(1)
        c = card.contentLayout()
        r1 = FormRow('串口端口')
        self.ln_port = SerialPortComboBox(self)
        self.ln_port.currentTextChanged.connect(lambda t: t and config.set(config.Lightning_Port, t))
        self.ln_port.setCurrentText(config.get(config.Lightning_Port) or 'None')
        r1.setWidget(self.ln_port)
        c.addWidget(r1)
        r2 = FormRow('波特率')
        self.ln_baud = SpinBox(self)
        self.ln_baud.setRange(0, 2 ** 31 - 1)
        self.ln_baud.setValue(int(config.get(config.Lightning_Baudrate)))
        self.ln_baud.valueChanged.connect(lambda v: config.set(config.Lightning_Baudrate, v))
        r2.setWidget(self.ln_baud)
        c.addWidget(r2)
        r3 = FormRow('去抖窗口 (s)')
        self.ln_debounce = DoubleSpinBox(self)
        self.ln_debounce.setRange(0.05, 5)
        self.ln_debounce.setSingleStep(0.05)
        self.ln_debounce.setValue(float(config.get(config.Lightning_Debounce)))
        self.ln_debounce.valueChanged.connect(self._on_debounce)
        r3.setWidget(self.ln_debounce)
        c.addWidget(r3)
        tip = Label(text='触发路径: ① IO卡 ch0 硬件中断 ② 串口 JSON 流;\n'
                         '放电触发后生成固定缺陷类型"针孔缺陷", 显示在泳道第 5 道(橙色)', fontSize=11)
        tip.setStyleSheet(f'color:{Theme.ORANGE};background:transparent;')
        c.addWidget(tip)
        return card

    def _on_debounce(self, v):
        config.set(config.Lightning_Debounce, v)
        faultDetectionPipeline._lightning_debounce = float(v)

    # ================= IO 卡 =================
    def _build_iocard_card(self):
        card = Card('IO 卡与报警输出', self)
        self.io_chip = StatusChip('异常', 'err')
        card.headerExtraLayout().addWidget(self.io_chip)
        card.headerExtraLayout().addStretch(1)
        c = card.contentLayout()
        r1 = FormRow('报警输出通道')
        self.io_ch = QComboBox(self)
        self.io_ch.addItems([f'ch{i}' for i in range(8)])
        self.io_ch.setCurrentIndex(int(config.get(config.IOCard_WarningChannel)))
        self.io_ch.currentIndexChanged.connect(self._on_io_ch)
        r1.setWidget(self.io_ch)
        c.addWidget(r1)
        r2 = FormRow('报警持续时间 (s)')
        self.io_dur = DoubleSpinBox(self)
        self.io_dur.setRange(0.5, 60)
        self.io_dur.setValue(float(config.get(config.IOCard_WarningDuration)))
        self.io_dur.valueChanged.connect(self._on_io_dur)
        r2.setWidget(self.io_dur)
        c.addWidget(r2)
        r3 = FormRow('节流间隔 (s)')
        self.io_int = DoubleSpinBox(self)
        self.io_int.setRange(0.5, 60)
        self.io_int.setValue(float(config.get(config.IOCard_WarningInterval)))
        self.io_int.valueChanged.connect(self._on_io_int)
        r3.setWidget(self.io_int)
        c.addWidget(r3)
        in_row = QHBoxLayout()
        in_row.addWidget(Label(text='输入 IN0-7', fontSize=12))
        self.io_in = _IOLights(lambda: faultDetectionPipeline.IOCard().getInputData(), self)
        in_row.addWidget(self.io_in, 1)
        c.addLayout(in_row)
        tip = Label(text='输出 OUT0-3 = 光源频闪(占用) · 报警通道触发时拉低;\n'
                         'ch0-3 被频闪线程每 33ms 覆盖, 界面只读 IN、只动报警通道', fontSize=11)
        tip.setStyleSheet(f'color:{Theme.TXT2};background:transparent;')
        c.addWidget(tip)
        selftest = PushButton(self, text='IO 自检')
        selftest.clicked.connect(self._io_selftest)
        c.addWidget(selftest)
        return card

    def _on_io_ch(self, i):
        config.set(config.IOCard_WarningChannel, i)
        faultDetectionPipeline._warning_ch = int(i)

    def _on_io_dur(self, v):
        config.set(config.IOCard_WarningDuration, v)
        faultDetectionPipeline.warning_duration = int(v)

    def _on_io_int(self, v):
        config.set(config.IOCard_WarningInterval, v)
        faultDetectionPipeline.warning_interval = int(v)

    def _io_selftest(self):
        io = faultDetectionPipeline.IOCard()
        if getattr(io, 'lib', None) is None:
            QMessageBox.warning(self.window(), 'IO 自检', '未检测到 IO 卡')
            return
        ch = faultDetectionPipeline._warning_ch
        io.setOutPutData(**{f'ch{ch}': 0})
        threading.Timer(1.0, lambda: io.setOutPutData(**{f'ch{ch}': 1})).start()
        QMessageBox.information(self.window(), 'IO 自检', f'报警通道 ch{ch} 已拉低 1 秒')

    # ================= 刷新/默认 =================
    def _refresh(self):
        for row in self._camera_rows:
            row.refresh_state()
        self.light_chip.setState('ok' if faultDetectionPipeline.isLightSourceEnabled() else 'off',
                                 '已连接' if faultDetectionPipeline.isLightSourceEnabled() else '未启用')
        self.vsam_chip.setState('ok' if faultDetectionPipeline.isVSamplerEnabled() else 'off',
                                '已连接' if faultDetectionPipeline.isVSamplerEnabled() else '未启用')
        self.lightning_chip.setState('ok' if faultDetectionPipeline.isLightningEnabled() else 'off',
                                     '已启用' if faultDetectionPipeline.isLightningEnabled() else '未启用')
        self.io_chip.setState('ok' if getattr(faultDetectionPipeline.IOCard(), 'lib', None) else 'err',
                              '正常' if getattr(faultDetectionPipeline.IOCard(), 'lib', None) else '异常')
        self.vsam_info.setText(f'实时: 速度 {faultDetectionPipeline.velocity():.2f} m/s · '
                               f'累计 {faultDetectionPipeline.accumulatedDistance():.2f} m')
        mc = faultDetectionPipeline.modelConfig()
        if mc is not None:
            groups = {}
            for cam, g in mc.exposureBatch.items():
                groups.setdefault(g, []).append(cam[-1])
            self._group_label.setText('  '.join(f'批次{i + 1}: 相机{",".join(ns)}'
                                                for i, ns in sorted(groups.items())))
        else:
            self._group_label.setText('未选择型号配置')
        self.io_in.update()

    def _restore_defaults(self):
        if QMessageBox.question(self.window(), '恢复默认',
                                '将恢复串口/波特率/曝光/触发等默认值, 是否继续?',
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        config.set(config.VSampler_Baudrate, 115200)
        config.set(config.VSampler_Port, 'COM3')
        config.set(config.VSampler_Perimeter, 0.2)
        config.set(config.VSampler_Direction, False)
        config.set(config.Lightning_Baudrate, 115200)
        config.set(config.Lightning_Port, 'COM4')
        config.set(config.Lightning_Debounce, 0.3)
        config.set(config.LightSource_Baudrate, 19200)
        config.set(config.LightSource_Port, 'COM5')
        config.set(config.LightSource_Levels, [128] * 4)
        config.set(config.Camera_Triggers, [True] * 4)
        config.set(config.Camera_Exposures, [2000] * 4)
        config.set(config.IOCard_WarningChannel, 4)
        config.set(config.IOCard_WarningDuration, 3)
        config.set(config.IOCard_WarningInterval, 3)
        QMessageBox.information(self.window(), '恢复默认', '已恢复, 需重启设备连接生效')
