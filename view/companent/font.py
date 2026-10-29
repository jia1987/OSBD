from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget

# 全局字号补偿: 界面字体普遍偏小, 所有经 getFont/setFont 创建的字体统一 +2px
# (调用处传入的 fontSize 仍表示"设计字号", 放大只在这里做, 便于整体回调)
FONT_SIZE_OFFSET = 2


def setFont(widget: QWidget, fontSize=14, weight=QFont.Normal):
    """ set the font of widget

    Parameters
    ----------
    widget: QWidget
        the widget to set font

    fontSize: int
        font pixel size

    weight: `QFont.Weight`
        font weight
    """
    widget.setFont(getFont(fontSize, weight))


def getFont(fontSize=14, weight=QFont.Normal):
    """ create font

    Parameters
    ----------
    fontSize: int
        font pixel size

    weight: `QFont.Weight`
        font weight
    """
    font = QFont()
    font.setFamilies(['Segoe UI', 'Microsoft YaHei', 'PingFang SC'])
    font.setPixelSize(fontSize + FONT_SIZE_OFFSET)
    font.setWeight(weight)
    return font



