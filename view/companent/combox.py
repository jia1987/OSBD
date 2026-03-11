from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QComboBox
from typing import Iterator,Iterable
import serial
from .utils import loadQss
from .font import setFont
from core.database import UserManager
class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/combox.qss')
        setFont(self)
        self._items = []

    def _adjust(self):
        text = self.currentText()
        items = self._items.copy()
        if text in items:
            idx = items.index(text)
            for i in range(idx):
                self.removeItem(0)
            for i in range(len(items) - idx - 1):
                self.removeItem(1)
            self.insertItems(1, items[idx + 1:])
            self.insertItems(0, items[:idx])
        else:
            self.clear()
            self.addItems(items)

    def setItems(self, items: Iterable[str]):
        self._items = [i for i in items]
        self._adjust()
        self.update()

    def showPopup(self):
        """ 动态加载Items """
        self._adjust()
        super(ComboBox, self).showPopup()  # 弹出选项框


class SerialPortComboBox(ComboBox):
    def __init__(self, parent=None):
        super(SerialPortComboBox, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/combox.qss')

    def showPopup(self):
        """ 动态加载Items """
        # 获取接入的所有串口信息，插入combobox的选项中
        posts = [port.device for port in serial.tools.list_ports.comports()]
        self.setItems(['None'] + posts)
        super(SerialPortComboBox, self).showPopup()  # 弹出选项框


class UsersComboBox(ComboBox):
    def __init__(self, parent=None):
        super(UsersComboBox, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/combox.qss')
        self.manager = UserManager()
        self.setItems(self.manager.getAllUsernames())

    def showPopup(self):
        """ 动态加载Items """
        # 获取接入的所有串口信息，插入combobox的选项中
        self.setItems(self.manager.getAllUsernames())
        super(UsersComboBox, self).showPopup()  # 弹出选项框