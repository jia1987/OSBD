from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPointF, QPropertyAnimation, pyqtProperty,pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
import sys


class ToggleButton(QWidget):
    clicked = pyqtSignal()
    toogled = pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False
        self._position = 0.0  # 动画位置 0~1
        self.animation = QPropertyAnimation(self, b"position", self)
        self.animation.setDuration(200)

        self.setFixedSize(55, 30)

    def mousePressEvent(self, event):
        self.setChecked(not self._checked)
        super().mousePressEvent(event)
        self.clicked.emit()

    def setChecked(self, state: bool):
        if self._checked != state:
            self._checked = state
            self.animation.stop()
            self.animation.setEndValue(1.0 if state else 0.0)
            self.animation.start()
            self.update()
            self.toogled.emit(state)

    def isChecked(self):
        return self._checked

    def getPosition(self):
        return self._position

    def setPosition(self, pos):
        self._position = pos
        self.update()

    position = pyqtProperty(float, fget=getPosition, fset=setPosition)

    def paintEvent(self, event):
        radius = self.height() / 2
        circle_radius = radius - 3

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景颜色
        if self._checked:
            bg_color = QColor(76, 217, 100)  # iOS 绿色
        else:
            bg_color = QColor(180, 180, 180)  # 灰色

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)

        # 背景圆角矩形
        painter.drawRoundedRect(0, 0, self.width(), self.height(), radius, radius)

        # 滑块位置
        x = 3 + self._position * (self.width() - 2 * (circle_radius + 3))

        # 滑块
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(QPointF(x + circle_radius, circle_radius + 3), circle_radius, circle_radius)


# 示例窗口
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom iOS Toggle Switch")

        self.toggle = ToggleButton(self)
        self.toggle.move(20, 20)
        self.toggle.setChecked(False)  # 设定初始状态

        self.resize(150, 80)

        # 监听状态变化
        self.toggle.animation.finished.connect(self.on_toggle_changed)

    def on_toggle_changed(self):
        print("当前开关状态:", self.toggle.isChecked())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
