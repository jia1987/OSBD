from PyQt5.QtWidgets import QListWidget,QListView
from .font import setFont
from .utils import loadQss


class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/list_view.qss')
        setFont(self)


class ListView(QListView):
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/list_view.qss')
        setFont(self)