from typing import Union

from PyQt5.QtCore import QRectF, QSize
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QToolButton

from .font import setFont
from .utils import loadQss
from .icon import drawIcon,Icon

class PushButton(QPushButton):

    def __init__(self, parent: QWidget = None, text: str = ""):
        super().__init__(text, parent)
        loadQss(w=self, path=r'_rc/qss/button.qss')
        self.isPressed = False
        self.isHover = False
        self.setIconSize(QSize(16, 16))
        self.setIcon(None)
        setFont(self)
        self._postInit()

    def _postInit(self):
        pass

    def setIcon(self, icon: Union[QIcon, str]):
        if icon is None or (isinstance(icon, QIcon) and icon.isNull()):
            self.setProperty('hasIcon', False)
        else:
            self.setProperty('hasIcon', True)

        self.setStyle(QApplication.style())
        self._icon = icon or QIcon()
        self.update()

    # def icon(self):
    #     return toQIcon(self._icon)

    def setProperty(self, name: str, value) -> bool:
        if name != 'icon':
            return super().setProperty(name, value)

        self.setIcon(value)
        return True

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def enterEvent(self, e):
        self.isHover = True
        self.update()

    def leaveEvent(self, e):
        self.isHover = False
        self.update()

    def _drawIcon(self, icon, painter, rect, state=QIcon.Off):
        """ draw icon """
        drawIcon(icon, painter, rect, state)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self.icon().isNull():
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if not self.isEnabled():
            painter.setOpacity(0.3628)
        elif self.isPressed:
            painter.setOpacity(0.786)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        mw = self.minimumSizeHint().width()
        if mw > 0:
            x = 12 + (self.width() - mw) // 2
        else:
            x = 12

        if self.isRightToLeft():
            x = self.width() - w - x

        self._drawIcon(self._icon, painter, QRectF(x, y, w, h))


class ToolButton(QToolButton):
    """ Tool button

    Constructors
    ------------
    * ToolButton(`parent`: QWidget = None)
    * ToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """

    def __init__(self, parent: QWidget = None, icon: Icon = None, text: str = ""):
        super().__init__(parent)
        loadQss(w=self, path=r'_rc/qss/button.qss')
        self.isPressed = False
        self.isHover = False
        self.setIconSize(QSize(16, 16))
        self.setIcon(icon)
        setFont(self)
        self._postInit()

    def _postInit(self):
        pass

    def setIcon(self, icon: Union[QIcon, str]):
        self._icon = icon
        self.update()

    def setProperty(self, name: str, value) -> bool:
        if name != 'icon':
            return super().setProperty(name, value)

        self.setIcon(value)
        return True

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def enterEvent(self, e):
        self.isHover = True
        self.update()

    def leaveEvent(self, e):
        self.isHover = False
        self.update()

    def _drawIcon(self, icon, painter: QPainter, rect: QRectF, state=QIcon.Off):
        """ draw icon """
        drawIcon(icon, painter, rect, state)

    def paintEvent(self, e):
        super().paintEvent(e)
        if self._icon is None:
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if not self.isEnabled():
            painter.setOpacity(0.43)
        elif self.isPressed:
            painter.setOpacity(0.63)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        x = (self.width() - w) / 2
        self._drawIcon(self._icon, painter, QRectF(x, y, w, h))
