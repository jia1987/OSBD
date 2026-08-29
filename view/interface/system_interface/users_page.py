""" 系统设置-用户管理: 用户表 + 创建/重置密码/禁用 (仅管理员可操作) """
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
                             QMessageBox, QInputDialog, QDialog, QLineEdit, QComboBox)

from ...companent import Label, PushButton
from ...common import Theme
from ...session import Session
from core.database import UserManager, Role


class CreateUserDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateUserDialog, self).__init__(parent)
        self.setWindowTitle('创建用户')
        self.setFixedWidth(320)
        layout = QVBoxLayout(self)
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setPlaceholderText('用户名')
        self.pwdEdit = QLineEdit(self)
        self.pwdEdit.setPlaceholderText('密码')
        self.pwdEdit.setEchoMode(QLineEdit.Password)
        self.roleCombo = QComboBox(self)
        self.roleCombo.addItems([r.e2c() for r in Role])
        layout.addWidget(self.nameEdit)
        layout.addWidget(self.pwdEdit)
        layout.addWidget(self.roleCombo)
        btns = QHBoxLayout()
        ok = PushButton(self, text='创建')
        ok.clicked.connect(self.accept)
        cancel = PushButton(self, text='取消')
        cancel.clicked.connect(self.reject)
        btns.addStretch(1)
        btns.addWidget(cancel)
        btns.addWidget(ok)
        layout.addLayout(btns)


class UsersPage(QWidget):
    def __init__(self, parent=None):
        super(UsersPage, self).__init__(parent)
        self._manager = UserManager()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        head = QHBoxLayout()
        head.addWidget(Label(text='用户管理', fontSize=14, weight=QFont.Bold))
        head.addStretch(1)
        self.create_btn = PushButton(self, text='+ 创建用户')
        self.create_btn.clicked.connect(self._create)
        self.create_btn.setVisible(Session.is_admin)
        head.addWidget(self.create_btn)
        layout.addLayout(head)

        self._model = QStandardItemModel(0, 5, self)
        self._model.setHorizontalHeaderLabels(['用户名', '角色', '创建时间', '最近登录', '状态'])
        self._table = QTableView(self)
        self._table.setModel(self._model)
        self._table.setEditTriggers(QTableView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self._table, 1)

        btns = QHBoxLayout()
        self.reset_btn = PushButton(self, text='重置密码')
        self.reset_btn.clicked.connect(self._reset_pwd)
        self.disable_btn = PushButton(self, text='禁用/启用')
        self.disable_btn.clicked.connect(self._toggle_enabled)
        btns.addStretch(1)
        btns.addWidget(self.reset_btn)
        btns.addWidget(self.disable_btn)
        layout.addLayout(btns)
        self.refresh()

    def refresh(self):
        self._model.removeRows(0, self._model.rowCount())
        for u in self._manager.listUsers():
            self._model.appendRow([
                QStandardItem(u['username']),
                QStandardItem(u['role'].e2c()),
                QStandardItem((u['createdAt'] or '')[:19]),
                QStandardItem((u['lastLogin'] or '从未')[:19]),
                QStandardItem('正常' if u['enabled'] else '已禁用'),
            ])

    def _selected_username(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        return self._model.item(rows[0].row(), 0).text()

    def _create(self):
        dlg = CreateUserDialog(self.window())
        if dlg.exec_() != QDialog.Accepted:
            return
        ok, msg = self._manager.createUser(
            Session.role, dlg.nameEdit.text(), dlg.pwdEdit.text(),
            Role(Role.c2e(dlg.roleCombo.currentText())))
        (QMessageBox.information if ok else QMessageBox.warning)(self.window(), '创建用户', msg)
        self.refresh()

    def _reset_pwd(self):
        name = self._selected_username()
        if not name:
            return
        pwd, ok = QInputDialog.getText(self.window(), '重置密码', f'新密码 ({name})',
                                       QLineEdit.Password)
        if not ok or not pwd:
            return
        ok, msg = self._manager.resetPassword(Session.role, name, pwd)
        (QMessageBox.information if ok else QMessageBox.warning)(self.window(), '重置密码', msg)

    def _toggle_enabled(self):
        name = self._selected_username()
        if not name:
            return
        cur = None
        for u in self._manager.listUsers():
            if u['username'] == name:
                cur = u['enabled']
        ok, msg = self._manager.setUserEnabled(Session.role, name, not cur)
        (QMessageBox.information if ok else QMessageBox.warning)(self.window(), '禁用/启用', msg)
        self.refresh()


