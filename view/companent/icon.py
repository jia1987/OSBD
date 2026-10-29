import os
from enum import Enum
from typing import Union

from PyQt5.QtCore import QRectF, QFile, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtXml import QDomDocument

from core.const import Path
from functools import cache

class Icon(Enum):
    SETTING = 'setting.svg'
    DETECTION = 'detection.svg'
    HISTORY = 'history.svg'
    DARABASE = 'database.svg'

    def path(self):
        return os.path.join(Path.ICON, self.value)

    def toQIcon(self, path: Union[str, None] = None) -> QIcon:
        path = path or self.path()
        return QIcon(path)

    def render(self, painter, rect, indexes=None, **attributes):
        """ draw svg icon """
        icon = self.path()
        if icon.endswith('.svg'):
            if attributes:
                # writeSvg 需要完整路径 (传相对文件名时 loadSvg 读不到内容 → 图标空白)
                icon = writeSvg(icon, indexes, **attributes).encode()
            drawSvgIcon(icon, painter, rect)
        else:
            icon = QIcon(self.toQIcon())
            rect = QRectF(rect).toRect()
            painter.drawPixmap(rect, icon.pixmap(QRectF(rect).toRect().size()))
@cache
def loadSvg(path):
    # 缓存文件内容而不是 QFile 对象:
    # QFile 被 close 后再读会得到空内容
    f = QFile(path)
    f.open(QFile.ReadOnly)
    data = bytes(f.readAll())
    f.close()
    return data

def writeSvg(iconPath: str, indexes=None, **attributes):
    """ write svg with specified attributes """
    if not iconPath.lower().endswith('.svg'):
        return ""

    dom = QDomDocument()
    dom.setContent(loadSvg(path=iconPath))

    # change the color of each path
    pathNodes = dom.elementsByTagName('path')
    indexes = range(pathNodes.length()) if not indexes else indexes
    for i in indexes:
        element = pathNodes.at(i).toElement()

        for k, v in attributes.items():
            element.setAttribute(k, v)

    return dom.toString()


def drawSvgIcon(icon, painter, rect):
    """ draw svg icon """
    renderer = QSvgRenderer(icon)
    renderer.render(painter, QRectF(rect))


def drawIcon(icon, painter, rect, state=QIcon.Off, **attributes):
    """ draw icon

    Parameters
    ----------
    icon: str | QIcon | FluentIconBaseBase
        the icon to be drawn

    painter: QPainter
        painter

    rect: QRect | QRectF
        the rect to render icon

    **attribute:
        the attribute of svg icon
    """
    if isinstance(icon, Icon):
        icon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        icon.paint(painter, QRectF(rect).toRect(), Qt.AlignCenter, state=state)
