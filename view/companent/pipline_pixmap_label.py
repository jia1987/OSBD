import time, cv2, os, json
import numpy as np
from PyQt5.QtWidgets import QLabel, QFontDialog
from PyQt5.QtGui import QPaintEvent, QPixmap, QPainter, QColor, QFontMetrics, QImage
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint, QTimer
from core import faultDetectionPipeline, ChannelInfo
from core.pipeline import FaultInfo
from core import utils
from .font import getFont
from functools import lru_cache
from PyQt5.QtGui import QColor


@lru_cache(maxsize=8)
def _build_lut(colormap: str):
    table = []

    for i in range(256):
        x = i / 255.0

        if colormap == "jds":
            r = 200 * x + 40
            g = 160 * x + 30
            b = 100 * x + 20

        elif colormap == "jet":
            r = min(max(1.5 - abs(4 * x - 3), 0), 1) * 255
            g = min(max(1.5 - abs(4 * x - 2), 0), 1) * 255
            b = min(max(1.5 - abs(4 * x - 1), 0), 1) * 255

        elif colormap == "hot":
            r = min(1, 3 * x) * 255
            g = min(1, max(0, 3 * x - 1)) * 255
            b = min(1, max(0, 3 * x - 2)) * 255

        elif colormap == "cool":
            r = x * 255
            g = (1 - x) * 255
            b = 255

        else:
            r = g = b = i

        table.append(QColor(
            int(min(255, r)),
            int(min(255, g)),
            int(min(255, b))
        ).rgb())

    return table


class PipelinePixmapLabelBase(QLabel):
    """ Base: 管线图像处理部分的显示Label """
    clicked = pyqtSignal(QPoint)

    @staticmethod
    def apply_colormap_to_pixmap(pixmap: QPixmap, colormap: str = "jds") -> QPixmap:
        img = pixmap.toImage()

        if img.format() != QImage.Format_Grayscale8:
            img = img.convertToFormat(QImage.Format_Grayscale8)

        img = img.convertToFormat(QImage.Format_Indexed8)

        img.setColorTable(_build_lut(colormap))

        return QPixmap.fromImage(img)

    def __init__(self, ctx: str, parent=None):
        self._ctx = ctx
        super(PipelinePixmapLabelBase, self).__init__(parent)
        assert isinstance(ctx, str), 'It must be a string'
        # 定时器驱动重绘(约30fps), 而不是在 paintEvent 里无条件 update()
        # 造成以屏幕刷新率持续全量重绘
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._onRefreshTimeout)
        self._refresh_timer.start(33)

    def _onRefreshTimeout(self):
        if self.isVisible():
            self.update()

    def paintEvent(self, event: QPaintEvent):
        super(PipelinePixmapLabelBase, self).paintEvent(event)

        # get image
        info = faultDetectionPipeline.channels(ctx=self._ctx)
        is_success = self._info_process(info=info)

        if not is_success:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.red)
            painter.setPen(Qt.white)
            painter.drawRect(self.rect())
            font = getFont(24, True)
            painter.setFont(font)
            mf = QFontMetrics(font)
            text = self.tr('无信号:') + self._ctx
            rect = mf.boundingRect(text)
            res = self.size() - rect.size()
            painter.drawText(res.width() // 2, res.height() // 2 + mf.ascent() + mf.descent(), text)

    def ctx(self):
        return self._ctx

    def mousePressEvent(self, e):
        super(PipelinePixmapLabelBase, self).mousePressEvent(e)
        self.clicked.emit(e.pos())

    def _info_process(self, info: ChannelInfo) -> QPixmap:
        raise NotImplementedError()


class PipelineCameraLabel(PipelinePixmapLabelBase):
    """ Base: 管线中相机部分的原始图像 """

    def _info_process(self, info: ChannelInfo) -> QPixmap:
        if info is None or info.camera is None:
            return False
        # 可能还没有采集到图像
        # 只读取一次, 避免两次 read 之间帧被更新导致丢帧/不一致
        np_img = info.camera.read()
        if np_img is None: return False
        image: QPixmap = utils.np_2_pixmap(arr=np_img)
        # resize
        if image.size() != self.size():
            image: QPixmap = image.scaled(self.size(), Qt.KeepAspectRatio)

        # Draw
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        res = self.size() - image.size()
        painter.drawPixmap(res.width() // 2, res.height() // 2, image)
        return True


class PipelineResultLabel(PipelinePixmapLabelBase):
    """ Base: 管线中经过处理的结果图像 """

    def __init__(self, ctx: str, parent=None):
        super(PipelineResultLabel, self).__init__(ctx=ctx, parent=parent)
        self._font = getFont(12)
        self._fm = QFontMetrics(self._font)

    def _info_process(self, info: ChannelInfo) -> QPixmap:
        if info is None or \
                info.detect_image is None or \
                info.faults is None:
            return None

        # color_img = cv2.applyColorMap(info.oringe_image, cv2.COLORMAP_JET)
        image: QPixmap = utils.np_2_pixmap(arr=info.oringe_image)
        image = self.apply_colormap_to_pixmap(pixmap=image)
        # resize
        if image.size() != self.size():
            resized_image: QPixmap = image.scaled(self.size(), Qt.KeepAspectRatio)
        else:
            resized_image = image

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        res = self.size() - resized_image.size()
        raito = resized_image.width() / image.width()
        offset = QPointF(res.width() // 2, res.height() // 2, )
        # draw
        painter.drawPixmap(offset, resized_image)
        painter.setPen(Qt.red)
        for fault in info.faults:
            painter.drawRect(QRectF(offset.x() + fault.x * raito, offset.y() + fault.y * raito,
                                    fault.w * raito, fault.h * raito))
            painter.drawText(QPointF(offset.x() + fault.x * raito,
                                     offset.y() + fault.y * raito - self._fm.descent() * 1.2),
                             fault.ftype)
        return True


class ResultLabel(PipelinePixmapLabelBase):
    """ 图像识别结果 """

    def __init__(self, parent=None):
        super(ResultLabel, self).__init__(ctx='result', parent=parent)
        self._pixmap = None
        self._faults = None
        self._font = getFont(12)
        self._fm = QFontMetrics(self._font)
        self._readPath = None
        self._offset = None
        self._ratio = None

    def setResult(self, path):
        # 可能不存在, 不存在则跳过
        self._readPath = path
        self._pixmap = None
        self._faults = None
        if path and os.path.exists(path):
            image_path = os.path.join(path, 'image.jpg')
            fault_path = os.path.join(path, 'fault.json')
            if os.path.exists(image_path):
                self._pixmap = QPixmap(image_path)
                self._pixmap = PipelinePixmapLabelBase.apply_colormap_to_pixmap(pixmap=self._pixmap)
            # fault.json 可能因断电等原因缺失或损坏, 不能直接打开
            if os.path.exists(fault_path):
                try:
                    with open(fault_path, 'r', encoding='utf-8') as f:
                        faults = json.load(f)
                    self._faults = FaultInfo.from_dict(**faults)
                except Exception as e:
                    print(f'[System] 加载缺陷记录失败 {fault_path}: {e}')
        self.update()

    def paintEvent(self, event: QPaintEvent):
        # 直接绘制缓存的结果图, 不走管线通道逻辑
        QLabel.paintEvent(self, event)
        if self._pixmap is None:
            return

        if self._pixmap.size() != self.size():
            resized_image: QPixmap = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio)
        else:
            resized_image = self._pixmap

        # draw to gui
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        res = self.size() - resized_image.size()
        raito = resized_image.width() / self._pixmap.width()
        offset = QPointF(res.width() // 2, res.height() // 2, )
        self._offset = offset
        self._ratio = raito
        # draw
        painter.drawPixmap(offset, resized_image)
        painter.setPen(Qt.red)
        if self._faults is not None:
            for fault in self._faults.faults:
                painter.drawRect(QRectF(offset.x() + fault.x * raito, offset.y() + fault.y * raito,
                                        fault.w * raito, fault.h * raito))
                painter.drawText(QPointF(offset.x() + fault.x * raito,
                                         offset.y() + fault.y * raito - self._fm.descent() * 1.2),
                                 fault.ftype)

    def faultIn(self, pos: QPoint) -> int:
        if self._faults is None:
            return -1
        if self._offset is not None:
            pos = pos - self._offset
        ratio = 1 if (self._ratio is None) else self._ratio
        for i, fault in enumerate(self._faults.faults):
            if fault.x <= pos.x() / ratio <= fault.x + fault.w and fault.y <= pos.y() / ratio <= fault.y + fault.h:
                return i
        return -1

    def _info_process(self, info: ChannelInfo) -> QPixmap:
        raise NotImplementedError()

    def readPath(self) -> str:
        return self._readPath
