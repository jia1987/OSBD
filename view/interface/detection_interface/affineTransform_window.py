import os.path
import json
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QPen, QPaintEvent
from PyQt5.QtCore import pyqtSlot, QTimer, QEvent, Qt, QPoint
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QSpacerItem
from PyQt5.QtWidgets import QComboBox, QInputDialog, QMessageBox, QPushButton, QLabel, QLineEdit, QSizePolicy, \
    QSpacerItem
from fontTools.misc.iterTools import batched
from functools import partial
from view.companent import PipelineCameraLabel, PipelineResultLabel, Label
from typing import List
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QWidget
from core import faultDetectionPipeline
from core.const import Path
from core import utils
from core import ModelConfig
from ...companent import Pivot, RangeSlider,PushButton


class SingleAffineTransformWidget(QWidget):
    _range_slider_maxmum = 10000

    def __init__(self, ctx: str, parent=None):
        self._ctx = ctx
        super(SingleAffineTransformWidget, self).__init__(parent)

        self.initWidget()
        self.initLayout()
        self.initData()
        self.initConnect()

    def initWidget(self):
        self.canvas = QWidget(self)
        self.canvas.installEventFilter(self)
        self.top_slider = RangeSlider(parent=self)
        self.bottom_slider = RangeSlider(parent=self)

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)

        self.viewLayout.addWidget(self.top_slider, alignment=Qt.AlignHCenter)
        self.viewLayout.addWidget(self.canvas, 1)
        self.viewLayout.addWidget(self.bottom_slider, alignment=Qt.AlignHCenter)

    def initData(self):
        self._set_slider_range(minmun=0, maxmun=self._range_slider_maxmum)

    def initConnect(self):
        self.top_slider.rangeChanged.connect(self.update)
        self.bottom_slider.rangeChanged.connect(self.update)

    def setValue(self, top_lower, top_upper, bottom_lower, bottom_upper):
        self.top_slider.setLowerValue(int(top_lower * self._range_slider_maxmum))
        self.top_slider.setUpperValue(int(top_upper * self._range_slider_maxmum))
        self.bottom_slider.setLowerValue(int(bottom_lower * self._range_slider_maxmum))
        self.bottom_slider.setUpperValue(int(bottom_upper * self._range_slider_maxmum))
        self.update()

    def _set_slider_width(self, width):
        self.top_slider.setFixedWidth(width)
        self.bottom_slider.setFixedWidth(width)

    def _set_slider_range(self, minmun, maxmun):
        self.top_slider.setRange(minmun, maxmun)
        self.bottom_slider.setRange(minmun, maxmun)


    def paintEvent(self, e:QPaintEvent):
        super(SingleAffineTransformWidget, self).paintEvent(e)

        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
    def eventFilter(self, obj, e: QEvent):
        # 绘制
        if obj is self.canvas and e.type() == QEvent.Paint:
            info = faultDetectionPipeline.channels(ctx=self._ctx)
            painter = QPainter(self.canvas)
            painter.setRenderHint(QPainter.Antialiasing)
            if info.camera is not None:
                painter.eraseRect(self.rect())
                image_np = info.camera.read()
                pixmap = utils.np_2_pixmap(arr=image_np)
                # resize
                if pixmap.size() != self.canvas.size():
                    pixmap: QPixmap = pixmap.scaled(self.canvas.size(), Qt.KeepAspectRatio)

                res = self.canvas.size() - pixmap.size()
                offset = QPoint(res.width() // 2, res.height() // 2)
                painter.drawPixmap(offset, pixmap)

                # 绘制放射变换的tips
                painter.setPen(QPen(Qt.red, 3))
                painter.drawLine(
                    QPoint(
                        offset.x() + int(self.top_slider.lowerValue() / self._range_slider_maxmum * pixmap.width()),
                        offset.y()),
                    QPoint(
                        offset.x() + int(self.bottom_slider.lowerValue() / self._range_slider_maxmum * pixmap.width()),
                        offset.y() + pixmap.height()))
                painter.drawLine(
                    QPoint(
                        offset.x() + int(self.top_slider.upperValue() / self._range_slider_maxmum * pixmap.width()),
                        offset.y()),
                    QPoint(
                        offset.x() + int(self.bottom_slider.upperValue() / self._range_slider_maxmum * pixmap.width()),
                        offset.y() + pixmap.height()))

                self._set_slider_width(pixmap.width())

        return super(SingleAffineTransformWidget, self).eventFilter(obj, e)

    def value(self):
        top_lower = self.top_slider.lowerValue() / self._range_slider_maxmum
        top_upper = self.top_slider.upperValue() / self._range_slider_maxmum
        bottom_lower = self.bottom_slider.lowerValue() / self._range_slider_maxmum
        bottom_upper = self.bottom_slider.upperValue() / self._range_slider_maxmum
        return top_lower, top_upper, bottom_lower, bottom_upper


class AffineTransformWidget(QWidget):

    def __init__(self, parent=None):
        super(AffineTransformWidget, self).__init__(parent)

        self.initWidget()
        self.initLayout()
        self.initConnect()

    def initWidget(self):
        self.return_btn = PushButton(self,self.tr('返回'))
        self.save_btn = PushButton(self,self.tr('设置'))
        self.pivot = Pivot(parent=self)
        self.stackedWidget = QStackedWidget(self)

        # 每个相机单独设置放射变换
        self.singleAffineTransformWidget_list: List[SingleAffineTransformWidget] = []
        for i, (channel, _) in enumerate(zip(faultDetectionPipeline.CHANNELS,
                                               (1, 2, 3, 4))):
            w = SingleAffineTransformWidget(ctx=channel, parent=self)
            self.singleAffineTransformWidget_list.append(w)
            self.stackedWidget.addWidget(w)
            self.pivot.addButton(text=self.tr(f'通道{i}'),
                                 onClicked=partial(self.stackedWidget.setCurrentWidget, w))

    def initLayout(self):
        self.viewLayout = QVBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout1 = QHBoxLayout()

        self.viewLayout.addWidget(self.pivot)
        self.viewLayout.addWidget(self.stackedWidget, 1)

        self.hlayout1.addWidget(self.return_btn)
        self.hlayout1.addWidget(self.save_btn)
        self.viewLayout.addLayout(self.hlayout1)

    def initConnect(self):
        self.return_btn.clicked.connect(self.close)
        self.save_btn.clicked.connect(self._save_to_model_config)
        self.save_btn.clicked.connect(self.close)

    def setModelConfig(self, model_config: ModelConfig):
        self._model_config = model_config
        for single in self.singleAffineTransformWidget_list:
            top_lower, top_upper, bottom_lower, bottom_upper = model_config.rectification[single._ctx]
            single.setValue(top_lower=top_lower, top_upper=top_upper,
                            bottom_lower=bottom_lower, bottom_upper=bottom_upper)

    def _save_to_model_config(self):
        for single in self.singleAffineTransformWidget_list:
            top_lower, top_upper, bottom_lower, bottom_upper = single.value()

            self._model_config.rectification[single._ctx] = (top_lower, top_upper, bottom_lower, bottom_upper)

    def paintEvent(self, e):
        super(AffineTransformWidget, self).paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.white)
        painter.drawRoundedRect(self.rect(), 5, 5)
