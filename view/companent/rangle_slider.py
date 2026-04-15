from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor
import sys


from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor


class RangeSlider(QWidget):
    """ Fluent 风格双滑块 RangeSlider """
    rangeChanged = pyqtSignal(int, int)

    def __init__(self, minimum=0, maximum=100, parent=None):
        super().__init__(parent)

        self.setFixedHeight(24)
        self.setMouseTracking(True)

        # 数据
        self._minimum = minimum
        self._maximum = maximum
        self._lowerValue = minimum
        self._upperValue = maximum

        # 状态
        self._dragging = None   # 'lower' or 'upper'
        self._hover = None

        # 样式参数（Fluent）
        self._trackHeight = 4
        self._handleRadius = 6

    # ================= 数据接口 =================
    def setRange(self, min_val, max_val):
        self._minimum, self._maximum = min_val, max_val
        self._lowerValue, self._upperValue = min_val, max_val
        self.update()

    def lowerValue(self):
        return self._lowerValue

    def upperValue(self):
        return self._upperValue

    def setLowerValue(self, val):
        val = max(self._minimum, min(val, self._upperValue))
        if val != self._lowerValue:
            self._lowerValue = val
            self.update()
            self.rangeChanged.emit(self._lowerValue, self._upperValue)

    def setUpperValue(self, val):
        val = min(self._maximum, max(val, self._lowerValue))
        if val != self._upperValue:
            self._upperValue = val
            self.update()
            self.rangeChanged.emit(self._lowerValue, self._upperValue)

    # ================= 工具函数 =================
    def _valueToPos(self, value):
        """值 -> 像素"""
        ratio = (value - self._minimum) / (self._maximum - self._minimum)
        return int(ratio * self.width())

    def _posToValue(self, x):
        """像素 -> 值"""
        ratio = x / self.width()
        return int(self._minimum + ratio * (self._maximum - self._minimum))

    # ================= 绘制 =================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        bar_y = h // 2 - self._trackHeight // 2

        # 背景轨道
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(220, 220, 220, 160))
        painter.drawRoundedRect(0, bar_y, w, self._trackHeight, 2, 2)

        # 位置
        lower_x = self._valueToPos(self._lowerValue)
        upper_x = self._valueToPos(self._upperValue)

        # 选中区域
        painter.setBrush(QColor(0, 120, 215))
        painter.drawRoundedRect(lower_x, bar_y, upper_x - lower_x, self._trackHeight, 2, 2)

        # 画滑块
        self._drawHandle(painter, lower_x, h, "lower")
        self._drawHandle(painter, upper_x, h, "upper")

    def _drawHandle(self, painter, x, h, which):
        r = self._handleRadius

        active = (self._dragging == which)
        hover = (self._hover == which)

        # 阴影
        painter.setBrush(QColor(0, 0, 0, 30))
        painter.drawEllipse(x - r, h // 2 - r, r * 2, r * 2)

        # 颜色
        if active:
            color = QColor(0, 120, 215)
        elif hover:
            color = QColor(240, 240, 240)
        else:
            color = QColor(255, 255, 255)

        # 内圆
        painter.setBrush(color)
        painter.drawEllipse(x - r + 1, h // 2 - r + 1, (r - 1) * 2, (r - 1) * 2)

    # ================= 事件 =================
    def mousePressEvent(self, event):
        x = event.x()

        lower_x = self._valueToPos(self._lowerValue)
        upper_x = self._valueToPos(self._upperValue)

        # 选最近的滑块
        if abs(x - lower_x) < abs(x - upper_x):
            self._dragging = "lower"
        else:
            self._dragging = "upper"

    def mouseMoveEvent(self, event):
        x = max(0, min(event.x(), self.width()))

        lower_x = self._valueToPos(self._lowerValue)
        upper_x = self._valueToPos(self._upperValue)

        # Hover 判断
        if abs(x - lower_x) < 10:
            self._hover = "lower"
        elif abs(x - upper_x) < 10:
            self._hover = "upper"
        else:
            self._hover = None

        # 拖动
        if self._dragging:
            value = self._posToValue(x)
            if self._dragging == "lower":
                self.setLowerValue(value)
            else:
                self.setUpperValue(value)

        self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = None
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QWidget()
    win.setWindowTitle("双滑块 RangeSlider Demo")

    slider = RangeSlider(0, 100)
    slider.setLowerValue(20)
    slider.setUpperValue(80)

    def on_range_changed(l, u):
        print(f"范围: {l} - {u}")

    slider.rangeChanged.connect(on_range_changed)

    # 简单布局
    from PyQt5.QtWidgets import QVBoxLayout
    layout = QVBoxLayout(win)
    layout.addWidget(slider)

    win.show()
    sys.exit(app.exec_())
