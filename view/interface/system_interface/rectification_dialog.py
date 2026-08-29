""" 透视矫正 (仿射变换) 升级弹窗: 画布上直接拖拽 4 端点, 红线实时叠加
值域归一化 0~1, 仅写内存 ModelConfig.rectification, 落盘沿用"保存/使用配置" """
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QColor, QPainter, QPen, QFont
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QPushButton)

from ...companent import Label
from ...common import Theme
from core import faultDetectionPipeline, utils
from core.pipeline.meta import PipelineType

HANDLE_R = 8


class RectCanvas(QWidget):
    """ 相机画面 + 4 端点拖拽 (top_lower, top_upper, bottom_lower, bottom_upper) """

    def __init__(self, ctx: str, model_config, parent=None):
        super(RectCanvas, self).__init__(parent)
        self._ctx = ctx
        self._mc = model_config
        self._pixmap = None
        self._drag = None  # 0..3
        self.setMinimumHeight(280)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(33)

    def _values(self):
        return list(self._mc.rectification.get(self._ctx, (0, 1, 0, 1)))

    def _set_value(self, idx, v):
        vals = self._values()
        vals[idx] = max(0.0, min(1.0, v))
        # 保持 top_lower <= top_upper / bottom_lower <= bottom_upper
        if idx == 0:
            vals[0] = min(vals[0], vals[1])
        if idx == 1:
            vals[1] = max(vals[1], vals[0])
        if idx == 2:
            vals[2] = min(vals[2], vals[3])
        if idx == 3:
            vals[3] = max(vals[3], vals[2])
        self._mc.rectification[self._ctx] = tuple(vals)
        self.update()

    def _handle_positions(self):
        w, h = self.width(), self.height()
        tl, tu, bl, bu = self._values()
        return [QPointF(tl * w, 8), QPointF(tu * w, 8),
                QPointF(bl * w, h - 8), QPointF(bu * w, h - 8)]

    def _refresh(self):
        info = faultDetectionPipeline.channels(ctx=self._ctx)
        if info is not None and info.camera is not None:
            img = info.camera.read()
            if img is not None:
                self._pixmap = utils.np_2_pixmap(arr=img)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(Theme.IMAGE))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        if self._pixmap is not None:
            scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio)
            off = QPointF((self.width() - scaled.width()) / 2,
                          (self.height() - scaled.height()) / 2)
            painter.drawPixmap(off, scaled)
        # 红线: 左上↔左下, 右上↔右下
        pos = self._handle_positions()
        painter.setPen(QPen(QColor(Theme.RED), 3))
        painter.drawLine(pos[0], pos[2])
        painter.drawLine(pos[1], pos[3])
        # 端点
        for p in pos:
            painter.setPen(QPen(QColor('#FFFFFF'), 2))
            painter.setBrush(QColor(Theme.ACCENT))
            painter.drawEllipse(p, HANDLE_R, HANDLE_R)

    # ---- 拖拽 ----
    def _hit(self, pos):
        for i, p in enumerate(self._handle_positions()):
            if (pos - p).manhattanLength() < HANDLE_R * 2:
                return i
        return None

    def mousePressEvent(self, event):
        self._drag = self._hit(event.pos())

    def mouseMoveEvent(self, event):
        if self._drag is None:
            return
        self._set_value(self._drag, event.x() / max(1, self.width()))

    def mouseReleaseEvent(self, event):
        self._drag = None


class RectificationDialog(QDialog):
    def __init__(self, model_config, parent=None):
        super(RectificationDialog, self).__init__(parent)
        self._mc = model_config
        self.setWindowTitle('透视矫正 (仿射变换)')
        self.resize(880, 560)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        head = QHBoxLayout()
        head.addWidget(Label(text='透视矫正', fontSize=15, weight=QFont.Bold))
        head.addStretch(1)
        self.channelCombo = QComboBox(self)
        self.channelCombo.addItems([f'通道{i + 1}' for i in range(len(PipelineType.CHANNELS))])
        head.addWidget(self.channelCombo)
        layout.addLayout(head)

        self._canvas = None
        self._canvas_wrap = QVBoxLayout()
        layout.addLayout(self._canvas_wrap, 1)
        self.channelCombo.currentIndexChanged.connect(self._switch_channel)
        self._switch_channel(0)

        tip = Label(text='拖拽蓝色端点调整红色引导线; 参数归一化保存, 仅写入内存, '
                         '需经"型号管理-保存/使用配置"落盘', fontSize=11)
        tip.setStyleSheet(f'color:{Theme.ORANGE};background:transparent;')
        layout.addWidget(tip)

        btns = QHBoxLayout()
        back = QPushButton('返回', self)
        back.clicked.connect(self.reject)
        apply_btn = QPushButton('应用矫正参数', self)
        apply_btn.setStyleSheet(
            f'background:{Theme.ACCENT};color:#FFFFFF;border:none;border-radius:6px;'
            f'padding:8px 20px;font-weight:bold;')
        apply_btn.clicked.connect(self.accept)
        btns.addStretch(1)
        btns.addWidget(back)
        btns.addWidget(apply_btn)
        layout.addLayout(btns)

    def _switch_channel(self, idx):
        if self._canvas is not None:
            self._canvas._timer.stop()
            self._canvas.deleteLater()
        ctx = PipelineType.CHANNELS[idx]
        self._canvas = RectCanvas(ctx, self._mc, self)
        self._canvas_wrap.addWidget(self._canvas)

    def closeEvent(self, event):
        if self._canvas is not None:
            self._canvas._timer.stop()
        super(RectificationDialog, self).closeEvent(event)
