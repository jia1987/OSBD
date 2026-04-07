import time
import os
import json
import numpy as np
from PyQt5.QtWidgets import QLabel, QFontDialog
from PyQt5.QtGui import QPaintEvent, QPixmap, QPainter, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QPointF
from core import faultDetectionPipeline, ChannelInfo
from core import utils
from core.pipeline import FaultInfo
from ...companent.font import getFont
from ...companent.pipline_pixmap_label import PipelinePixmapLabelBase

#
# class ResultLabel(QLabel):
#     """ 图像识别结果 """
#     def __init__(self, parent=None):
#         super(ResultLabel, self).__init__(parent)
#         self._pixmap = None
#         self._font = getFont(12)
#         self._fm = QFontMetrics(self._font)
#
#     def setResult(self, path):
#         # 可能不存在, 不存在则跳过
#         if not os.path.exists(path):
#             self._pixmap = None
#         else:
#             self._pixmap = QPixmap(os.path.join(path, 'image.jpg'))
#             self._pixmap =  PipelinePixmapLabelBase.apply_colormap_to_pixmap(pixmap=self._pixmap)
#
#             with open(os.path.join(path, 'fault.json'), 'r', encoding='utf-8') as f:
#                 faults = json.load(f)
#                 self._faults = FaultInfo.from_dict(**faults)
#         self.update()
#
#     def paintEvent(self, event: QPaintEvent):
#         super(ResultLabel, self).paintEvent(event)
#         if self._pixmap is None:
#             return
#
#         if self._pixmap.size() != self.size():
#             resized_image: QPixmap = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio)
#         else:
#             resized_image = self._pixmap
#
#
#         # draw to gui
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.Antialiasing)
#         res = self.size() - resized_image.size()
#         raito = resized_image.width() / self._pixmap.width()
#         offset = QPointF(res.width() // 2, res.height() // 2, )
#         # draw
#         painter.drawPixmap(offset, resized_image)
#         painter.setPen(Qt.red)
#         for fault in self._faults.faults:
#             painter.drawRect(QRectF(offset.x() + fault.x * raito, offset.y() + fault.y * raito,
#                                     fault.w * raito, fault.h * raito))
#             painter.drawText(QPointF(offset.x() + fault.x * raito,
#                                      offset.y() + fault.y * raito - self._fm.descent() * 1.2),
#                              fault.ftype)
#
#     def _info_process(self, info: ChannelInfo) -> QPixmap:
#         raise NotImplementedError()
