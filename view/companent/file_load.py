from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QTextEdit, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog


class FileLoadBox(QWidget):
    pathChanged = pyqtSignal(str)

    def __init__(self, parent, filter='All Files (*)', title='选择文件'):
        super(FileLoadBox, self).__init__(parent)
        self._filter = filter
        self._title = title
        self.textView = QTextEdit(self)
        self.textView.setAcceptRichText(False)
        self.textView.setEnabled(False)
        self.btn = QPushButton(self)
        self.btn.setText(self.tr("修改路径"))

        self.viewLayout = QHBoxLayout(self)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addWidget(self.textView)
        self.viewLayout.addWidget(self.btn)

        self.btn.clicked.connect(self._onClicked)
        self.textView.textChanged.connect(lambda :self.pathChanged.emit(self.textView.toPlainText()))
        fm = QFontMetrics(self.textView.font())
        self.textView.setFixedHeight(fm.height() + fm.descent() + fm.ascent())

    def setPath(self, path):
        self.textView.setText(path)

    def _onClicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.window(),
            self._title,
            "",
            self._filter
        )

        if not file_path:
            return
        self.textView.setText(file_path)

    def path(self):
        return self.textView.toPlainText()
