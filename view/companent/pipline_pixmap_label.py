import time
import numpy as np
from PyQt5.QtWidgets import QLabel, QFontDialog
from PyQt5.QtGui import QPaintEvent, QPixmap, QPainter, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QPointF,pyqtSignal,QPoint
from core import faultDetectionPipeline, ChannelInfo
from core import utils
from .font import getFont


class PipelinePixmapLabelBase(QLabel):
    """ Base: 管线图像处理部分的显示Label """
    clicked = pyqtSignal(QPoint)
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
    def mousePressEvent(self,e):
        super(PipelinePixmapLabelBase,self).mousePressEvent(e)
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
        if np_img is None:return False
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
        image: QPixmap = utils.np_2_pixmap(arr=info.oringe_image)
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


