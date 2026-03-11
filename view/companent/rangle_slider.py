from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor
import sys


class RangeSlider(QWidget):
    """ 范围滑块 """
    rangeChanged = pyqtSignal(int, int)  # 发射 (lower, upper)
    _barHeight = 6
    _handleRadius = 8
    def __init__(self, minimum=0, maximum=100, parent=None):

        super().__init__(parent)
        #self.setMinimumWidth(200)
        self.setFixedHeight(self._handleRadius*2)

        self._minimum = minimum
        self._maximum = maximum
        self._lowerValue = minimum
        self._upperValue = maximum



        self._dragging = None  # 'lower' or 'upper'

    def setRange(self, min_val, max_val):
        self._minimum, self._maximum = min_val, max_val
        self._lowerValue, self._upperValue = min_val, max_val
        self.update()

    def lowerValue(self):
        return self._lowerValue

    def upperValue(self):
        return self._upperValue

    def setLowerValue(self, val):
        self._lowerValue = max(self._minimum, min(val, self._upperValue))
        self.update()
        self.rangeChanged.emit(self._lowerValue, self._upperValue)

    def setUpperValue(self, val):
        self._upperValue = min(self._maximum, max(val, self._lowerValue))
        self.update()
        self.rangeChanged.emit(self._lowerValue, self._upperValue)

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        # 进度条背景
        bar_y = h // 2 - self._barHeight // 2
        painter.setBrush(QBrush(QColor(200, 200, 200)))
        painter.drawRect(0, bar_y, w, self._barHeight)

        # 计算滑块位置
        lower_x = int((self._lowerValue - self._minimum) / (self._maximum - self._minimum) * w)
        upper_x = int((self._upperValue - self._minimum) / (self._maximum - self._minimum) * w)

        # 选中范围
        painter.setBrush(QBrush(QColor(100, 180, 250)))
        painter.drawRect(lower_x, bar_y, upper_x - lower_x, self._barHeight)

        # 左滑块
        painter.setBrush(QBrush(QColor(50, 150, 250)))
        painter.drawEllipse(lower_x - self._handleRadius, h // 2 - self._handleRadius,
                            self._handleRadius * 2, self._handleRadius * 2)

        # 右滑块
        painter.setBrush(QBrush(QColor(50, 150, 250)))
        painter.drawEllipse(upper_x - self._handleRadius, h // 2 - self._handleRadius,
                            self._handleRadius * 2, self._handleRadius * 2)

    def mousePressEvent(self, event):
        x = event.x()
        w = self.width()
        lower_x = int((self._lowerValue - self._minimum) / (self._maximum - self._minimum) * w)
        upper_x = int((self._upperValue - self._minimum) / (self._maximum - self._minimum) * w)

        if abs(x - lower_x) < abs(x - upper_x):
            self._dragging = "lower"
        else:
            self._dragging = "upper"

    def mouseMoveEvent(self, event):
        if self._dragging:
            ratio = event.x() / self.width()
            value = int(self._minimum + ratio * (self._maximum - self._minimum))
            if self._dragging == "lower":
                self.setLowerValue(value)
            else:
                self.setUpperValue(value)

    def mouseReleaseEvent(self, event):
        self._dragging = None


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
