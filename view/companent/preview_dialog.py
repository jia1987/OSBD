""" 相机预览/试拍: 独立实例化 Camera(按 config 该路参数), 关闭即释放 """
import os
from datetime import datetime

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QHBoxLayout

from .button import PushButton
from core import utils
from core.config import config
from core.const import Path
from core.pipeline.device.camera import Camera, HK_Camera
from core.pipeline.error import CameraConnectError


class PreviewDialog(QDialog):
    def __init__(self, idx: int, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.setWindowTitle(f'相机{idx + 1} 预览')
        self.resize(720, 480)
        self._camera = None
        try:
            self._camera = Camera(
                read_mode=config.get(config.Camera_ReadModes)[idx],
                capture=config.get(config.Camera_Captures)[idx],
                img_path=config.get(config.Camera_Imgs)[idx],
                video_path=config.get(config.Camera_Videos)[idx],
                exposureTime=config.get(config.Camera_Exposures)[idx],
                port=config.get(config.Camera_Prots)[idx],
                device_list=HK_Camera.device_list())
        except CameraConnectError as e:
            QMessageBox.warning(parent, '预览', f'相机{idx + 1} 连接失败！\n{e}')
        except Exception as e:
            QMessageBox.warning(parent, '预览', f'相机{idx + 1} 初始化失败！\n{e}')

        layout = QVBoxLayout(self)
        self._label = QLabel('无信号', self)
        self._label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label, 1)
        btns = QHBoxLayout()
        self._snap_btn = PushButton(self, text='试拍保存')
        self._snap_btn.clicked.connect(self._snap)
        btns.addStretch(1)
        btns.addWidget(self._snap_btn)
        layout.addLayout(btns)

        self._last_pixmap = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        if self._camera is not None:
            self._timer.start(33)

    def _refresh(self):
        if self._camera is None:
            return
        img = self._camera.read()
        if img is None:
            return
        pix = utils.np_2_pixmap(arr=img)
        self._last_pixmap = pix
        self._label.setPixmap(pix.scaled(self._label.size(), Qt.KeepAspectRatio))

    def _snap(self):
        if self._last_pixmap is None:
            QMessageBox.warning(self, '试拍', '暂无画面')
            return
        debug_dir = os.path.join(Path.OUTPUT_DIR, 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        path = os.path.join(debug_dir, datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.jpg')
        self._last_pixmap.save(path)
        QMessageBox.information(self, '试拍', f'已保存:\n{path}')

    def closeEvent(self, event):
        self._timer.stop()
        if self._camera is not None:
            try:
                self._camera.close()
            except Exception as e:
                print(f'[System] 预览相机关闭失败: {e}')
        super(PreviewDialog, self).closeEvent(event)
