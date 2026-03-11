from typing import Callable

import serial
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtWidgets import QPushButton

from core.config import config
from core.pipeline import VSamplerSerialConnectError
from core.hk_camera.error import CameraInitError
from core.pipeline import faultDetectionPipeline, LightningSerialConnectError, LightSourceControlerSerialConnectError
from ...companent.font import setFont
from ...companent import PushButton


class EnableInterface(QWidget):

    def _change_serials_state(self,
                              btn: QPushButton,
                              control_text: str,
                              check_enable_func: Callable,
                              set_enable_func: Callable,
                              port,
                              title: str,
                              connect_error: Exception
                              ):
        # 检查是否能开启
        if not check_enable_func():
            if port == 'None':
                QMessageBox.warning(self.window(), self.tr(title), self.tr('未设置串口，无法启动！'))
                return
        try:
            set_enable_func(not check_enable_func())
        except serial.serialutil.SerialException as e:
            print(e)
            QMessageBox.warning(self.window(), self.tr(title), self.tr(f'{port}链接失败！'))
        except connect_error as e:
            print(e)
            QMessageBox.warning(self.window(), self.tr(title),
                                self.tr(f'{port}链接成功,但在初始化过程中失败！') + '\n' + str(e))
        except Exception as e:
            raise e
        btn.setText(self.tr(('关闭' if check_enable_func() else '启动') + control_text))

    def __init__(self, parent=None):
        super(EnableInterface, self).__init__(parent)

        self.initWidget()
        self.initConnect()
        self.initLayout()

    def initWidget(self):
        self.vsamplerBtn = PushButton(text=self.tr('启动计米'), parent=self)
        self.cameraBtn = PushButton(text=self.tr('启动摄像头'), parent=self)
        self.detectBtn = PushButton(parent=self, text=self.tr('启动检测'), )
        self.lightningBtn = PushButton(text=self.tr('启动放电检测'), parent=self)
        self.lightsourceBtn = PushButton(text=self.tr('启动光源'), parent=self)
        self.vsamplerBtn.setMinimumHeight(32)
        self.lightningBtn.setMinimumHeight(32)
        self.cameraBtn.setMinimumHeight(32)
        self.lightsourceBtn.setMinimumHeight(32)
        self.detectBtn.setMinimumHeight(64)
        setFont(self.detectBtn, fontSize=24)

    def initConnect(self):
        self.cameraBtn.clicked.connect(self._onCameraBtnCliked)
        self.detectBtn.clicked.connect(self._onDetectBtnCliked)
        self.vsamplerBtn.clicked.connect(lambda: print(123123123))
        self.vsamplerBtn.clicked.connect(lambda: self._change_serials_state(
            btn=self.vsamplerBtn,
            control_text='计米',
            check_enable_func=faultDetectionPipeline.isVSamplerEnabled,
            set_enable_func=faultDetectionPipeline.setVSamplerEnabled,
            port=config.get(config.VSampler_Port),
            title='计米',
            connect_error=VSamplerSerialConnectError
        ))
        self.lightningBtn.clicked.connect(lambda: self._change_serials_state(
            btn=self.lightningBtn,
            control_text='放电检测',
            check_enable_func=faultDetectionPipeline.isLightningEnabled,
            set_enable_func=faultDetectionPipeline.setLightningEnabled,
            port=config.get(config.Lightning_Port),
            title='放电检测',
            connect_error=LightningSerialConnectError
        ))
        self.lightsourceBtn.clicked.connect(lambda: self._change_serials_state(
            btn=self.lightsourceBtn,
            control_text='光源控制器',
            check_enable_func=faultDetectionPipeline.isLightSourceEnabled,
            set_enable_func=faultDetectionPipeline.setLightSourceEnable,
            port=config.get(config.LightSource_Port),
            title='光源控制器',
            connect_error=LightSourceControlerSerialConnectError
        ))

    def _onCameraBtnCliked(self):
        try:
            faultDetectionPipeline.setCameraEnabled(not faultDetectionPipeline.isCameraEnabled())
        except CameraInitError as e:
            QMessageBox.warning(self.window(), self.tr('启动摄像头'),
                                self.tr(f'摄像头初始化失败！') + '\n' + str(e))
        except Exception as e:
            raise e
        self.cameraBtn.setText(self.tr('启动摄像头' if not faultDetectionPipeline.isCameraEnabled() else '关闭摄像头'))


    def _onDetectBtnCliked(self):
        self.detectBtn.setText(self.tr('启动检测' if faultDetectionPipeline.isDetectEnabled() else '关闭检测'))
        faultDetectionPipeline.setDetectEnable(not faultDetectionPipeline.isDetectEnabled())

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        self.vsampler_lightning_btn_layout = QHBoxLayout()
        self.vsampler_lightning_btn_layout.addWidget(self.vsamplerBtn)
        self.vsampler_lightning_btn_layout.addWidget(self.lightningBtn)

        self.camera_lightsource_btn_layout = QHBoxLayout()
        self.camera_lightsource_btn_layout.addWidget(self.cameraBtn)
        self.camera_lightsource_btn_layout.addWidget(self.lightsourceBtn)

        self.viewLayout.addLayout(self.vsampler_lightning_btn_layout)
        self.viewLayout.addLayout(self.camera_lightsource_btn_layout)
        self.viewLayout.addWidget(self.detectBtn)

        self.viewLayout.setStretch(0, 1)
