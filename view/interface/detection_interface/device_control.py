""" 设备控制卡: 大启停按钮 + 4 设备开关
沿用历史异常分支文案: 未设置串口/链接失败/初始化失败/摄像头初始化失败 """
import serial.serialutil
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QMessageBox

from ...companent import PushButton
from ...companent.device_toggle_card import DeviceToggleCard
from ...common import Theme
from core import faultDetectionPipeline
from core.config import config
from core.hk_camera.error import CameraInitError
from core.pipeline.error import (VSamplerSerialConnectError,
                                 LightningSerialConnectError,
                                 LightSourceControlerSerialConnectError)


class DeviceControlCard(QWidget):
    def __init__(self, parent=None):
        super(DeviceControlCard, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ---- 大启停按钮 ----
        self.detectBtn = PushButton(self, text='启动检测')
        self.detectBtn.setMinimumHeight(46)
        self.detectBtn.clicked.connect(self._on_detect_clicked)
        layout.addWidget(self.detectBtn)

        # ---- 4 设备开关 ----
        grid = QGridLayout()
        grid.setSpacing(10)
        self.cameraCard = DeviceToggleCard('启动摄像头', self)
        self.lightCard = DeviceToggleCard('启动光源', self)
        self.vsamplerCard = DeviceToggleCard('启动计米', self)
        self.lightningCard = DeviceToggleCard('启动放电检测', self)
        grid.addWidget(self.cameraCard, 0, 0)
        grid.addWidget(self.lightCard, 0, 1)
        grid.addWidget(self.vsamplerCard, 1, 0)
        grid.addWidget(self.lightningCard, 1, 1)
        layout.addLayout(grid)

        self.cameraCard.toggle.clicked.connect(self._on_camera_clicked)
        self.vsamplerCard.toggle.clicked.connect(lambda: self._change_serials_state(
            '计米', config.VSampler_Port, faultDetectionPipeline.isVSamplerEnabled,
            faultDetectionPipeline.setVSamplerEnabled, VSamplerSerialConnectError, self.vsamplerCard))
        self.lightningCard.toggle.clicked.connect(lambda: self._change_serials_state(
            '放电检测', config.Lightning_Port, faultDetectionPipeline.isLightningEnabled,
            faultDetectionPipeline.setLightningEnabled, LightningSerialConnectError, self.lightningCard))
        self.lightCard.toggle.clicked.connect(lambda: self._change_serials_state(
            '光源控制器', config.LightSource_Port, faultDetectionPipeline.isLightSourceEnabled,
            faultDetectionPipeline.setLightSourceEnable, LightSourceControlerSerialConnectError, self.lightCard))

        self._sync_timer = QTimer(self)
        self._sync_timer.timeout.connect(self.sync_states)
        self._sync_timer.start(500)
        self.sync_states()

    # ================= 启停逻辑 =================
    def _change_serials_state(self, control_text, port_item, check_func, set_func, connect_error, card):
        port = config.get(port_item)
        # 串口未设置拦截 (沿用历史文案; port 点击时重读)
        if not check_func() and port == 'None':
            card.setState(False, '启动' + control_text)
            QMessageBox.warning(self.window(), self.tr(control_text), '未设置串口，无法启动！')
            return
        try:
            set_func(not check_func())
        except serial.serialutil.SerialException:
            QMessageBox.warning(self.window(), self.tr(control_text), f'{port}链接失败！')
        except connect_error as e:
            QMessageBox.warning(self.window(), self.tr(control_text),
                                f'{port}链接成功,但在初始化过程中失败！' + '\n' + str(e))
        except Exception as e:
            raise e
        self.sync_states()

    def _on_camera_clicked(self):
        try:
            faultDetectionPipeline.setCameraEnabled(not faultDetectionPipeline.isCameraEnabled())
        except CameraInitError as e:
            QMessageBox.warning(self.window(), self.tr('启动摄像头'), '摄像头初始化失败！' + '\n' + str(e))
        except Exception as e:
            raise e
        self.sync_states()

    def _on_detect_clicked(self):
        # 无确认框, 直接翻转
        faultDetectionPipeline.setDetectEnable(not faultDetectionPipeline.isDetectEnabled())
        self.sync_states()

    # ================= 状态同步 =================
    def sync_states(self):
        enabled = faultDetectionPipeline.isDetectEnabled()
        if enabled:
            self.detectBtn.setText('■  停止检测  (点击关闭)')
            self.detectBtn.setStyleSheet(
                f'PushButton, QPushButton{{background:{Theme.RED};color:#FFFFFF;border:none;border-radius:8px;font-size:16px;font-weight:bold;}}'
                f'QPushButton:hover{{background:#FF6B63;}}QPushButton:pressed{{background:#D6433C;}}')
        else:
            self.detectBtn.setText('▶  启动检测')
            self.detectBtn.setStyleSheet(
                f'QPushButton{{background:{Theme.GREEN};color:#FFFFFF;border:none;border-radius:8px;font-size:16px;font-weight:bold;}}'
                f'QPushButton:hover{{background:#43D07C;}}QPushButton:pressed{{background:#2AA35B;}}')

        self.cameraCard.setState(faultDetectionPipeline.isCameraEnabled(),
                                 ('关闭摄像头' if faultDetectionPipeline.isCameraEnabled() else '启动摄像头'))
        self.lightCard.setState(faultDetectionPipeline.isLightSourceEnabled(),
                                ('关闭光源' if faultDetectionPipeline.isLightSourceEnabled() else '启动光源'))
        self.vsamplerCard.setState(faultDetectionPipeline.isVSamplerEnabled(),
                                   ('关闭计米' if faultDetectionPipeline.isVSamplerEnabled() else '启动计米'))
        self.lightningCard.setState(faultDetectionPipeline.isLightningEnabled(),
                                    ('关闭放电检测' if faultDetectionPipeline.isLightningEnabled() else '启动放电检测'))
