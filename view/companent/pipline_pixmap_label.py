import time, cv2
import numpy as np
from PyQt5.QtWidgets import QLabel, QFontDialog
from PyQt5.QtGui import QPaintEvent, QPixmap, QPainter, QColor, QFontMetrics, QImage
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal, QPoint
from core import faultDetectionPipeline, ChannelInfo
from core import utils
from .font import getFont


class PipelinePixmapLabelBase(QLabel):
    """ Base: 管线图像处理部分的显示Label """
    clicked = pyqtSignal(QPoint)

    @staticmethod
    def apply_colormap_to_pixmap(pixmap: QPixmap, colormap: str = "jds") -> QPixmap:
        """
        灰度 QPixmap → 彩色 QPixmap（纯 Qt 实现）

        colormap: "jet" / "hot" / "cool" / "gray"
        """

        # === 转 QImage 并确保灰度格式 ===
        img = pixmap.toImage().convertToFormat(QImage.Format_Indexed8)

        # === 构造 LUT ===
        color_table = []

        for i in range(256):
            x = i / 255.0
            if colormap == "jds":
                # 🎯 核心：压缩对比度（变柔）
                x = 0.6 * x + 0.2  # 映射到 [0.2, 0.8]
                x = 1 - x
                # 🎯 暖色调映射（棕色系）
                r = (200 * x + 40) / 255
                g = (160 * x + 30) / 255
                b = (100 * x + 20) / 255

                # 限制范围
                r = min(1, r)
                g = min(1, g)
                b = min(1, b)
            elif colormap == "jet":
                r = min(max(1.5 - abs(4 * x - 3), 0), 1)
                g = min(max(1.5 - abs(4 * x - 2), 0), 1)
                b = min(max(1.5 - abs(4 * x - 1), 0), 1)

            elif colormap == "hot":
                r = min(1, 3 * x)
                g = min(1, max(0, 3 * x - 1))
                b = min(1, max(0, 3 * x - 2))

            elif colormap == "cool":
                r = x
                g = 1 - x
                b = 1

            else:  # gray
                r = g = b = x

            color_table.append(QColor(int(r * 255), int(g * 255), int(b * 255)).rgb())

        # === 应用 LUT（核心，零拷贝）===
        img.setColorTable(color_table)
        img.save('1.jpg')

        # === 转回 QPixmap ===
        return QPixmap.fromImage(img)

    def __init__(self, ctx: str, parent=None):
        self._ctx = ctx
        super(PipelinePixmapLabelBase, self).__init__(parent)
        assert isinstance(ctx, str), 'It must be a string'

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
        self.update()

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
        np_img = info.camera.read()
        if np_img is None: return False
        image: QPixmap = utils.np_2_pixmap(arr=info.camera.read())
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
