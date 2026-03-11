from PyQt5.QtWidgets import QTabWidget,QTableView
from .font import setFont
from .utils import loadQss


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/table_widget.qss')
        setFont(self)

class TableView(QTableView):
    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        loadQss(w=self, path=r'_rc/qss/table_widget.qss')
        setFont(self)