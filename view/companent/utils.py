from PyQt5.QtWidgets import QWidget
from functools import cache
@cache
def loadQssFile(path):
    with open(path, 'r', encoding='utf8') as f:
        s = f.read()
    return s
def loadQss(w: QWidget, path):
    w.setStyleSheet(loadQssFile(path))
