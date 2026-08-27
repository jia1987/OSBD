import os.path

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget,
    QMessageBox, QComboBox, QGroupBox, QFormLayout
)
from core.database import *
from core.pipeline import FaultInfo
from PyQt5.QtCore import Qt
from ...companent import PushButton, ComboBox, LineEdit, ListWidget, UsersComboBox
from core.const import Path



class UserManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = UserManager()
        self.currentUser = None
        self._initUi()

    def _initUi(self):
        mainLayout = QVBoxLayout(self)

        self._createLoginLayout(mainLayout)
        self._createBatchLayout(mainLayout)
        self._createAdminLayout(mainLayout)

        mainLayout.addStretch()

    # -----------------------
    # 登录区
    # -----------------------
    def _createLoginLayout(self, parentLayout):
        loginGroup = QGroupBox("登录")
        loginLayout = QFormLayout()

        self.userCombo = UsersComboBox()

        self.passwordEdit = LineEdit()
        self.passwordEdit.setEchoMode(LineEdit.Password)

        loginBtn = PushButton(self, "登录")
        loginBtn.clicked.connect(self._login)

        loginLayout.addRow("用户：", self.userCombo)
        loginLayout.addRow("密码：", self.passwordEdit)
        loginLayout.addRow(loginBtn)

        loginGroup.setLayout(loginLayout)
        parentLayout.addWidget(loginGroup)

    # -----------------------
    # 批次区
    # -----------------------
    def _createBatchLayout(self, parentLayout):
        batchGroup = QGroupBox("批次管理")
        batchLayout = QVBoxLayout()

        self.batchList = ListWidget()
        batchLayout.addWidget(self.batchList)

        hLayout = QHBoxLayout()
        self.batchEdit = LineEdit()
        self.batchEdit.setPlaceholderText("输入批次名称")

        # addBtn = PushButton(self, "添加批次")
        # addBtn.clicked.connect(self._addBatch)

        hLayout.addWidget(self.batchEdit)
        # hLayout.addWidget(addBtn)
        batchLayout.addLayout(hLayout)

        batchGroup.setLayout(batchLayout)
        parentLayout.addWidget(batchGroup)

    # -----------------------
    # 管理员区
    # -----------------------
    def _createAdminLayout(self, parentLayout):
        self.adminGroup = QGroupBox("管理员功能")
        adminLayout = QFormLayout()

        self.newUserEdit = LineEdit()
        self.newPwdEdit = LineEdit()
        self.newPwdEdit.setEchoMode(QLineEdit.Password)

        self.roleCombo = ComboBox()
        self.roleCombo.setItems([r.e2c() for r in Role])

        createBtn = PushButton(self, "创建用户")
        createBtn.clicked.connect(self._createUser)

        adminLayout.addRow("用户名：", self.newUserEdit)
        adminLayout.addRow("密码：", self.newPwdEdit)
        adminLayout.addRow("角色：", self.roleCombo)
        adminLayout.addRow(createBtn)

        self.adminGroup.setLayout(adminLayout)
        self.adminGroup.hide()

        parentLayout.addWidget(self.adminGroup)

    def _login(self):
        username = self.userCombo.currentText()
        password = self.passwordEdit.text()

        success, data = self.manager.login(username, password)
        if success:
            self.currentUser = data
            QMessageBox.information(self, "成功", "登录成功")
            self._refresh()
            if data["role"] == Role.ADMIN:
                self.adminGroup.show()
            else:
                self.adminGroup.hide()
        else:
            QMessageBox.warning(self, "错误", data)

    def _refresh(self):
        # user = self.manager.getUser(self.currentUser["id"])
        self.batchList.clear()
        items = []
        for bn in os.listdir(Path.OUTPUT_DIR):
            # batch name
            batchp = os.path.join(Path.OUTPUT_DIR, bn)
            # 0.0 0.1 0.3
            a_fp = tuple(os.listdir(batchp))
            if len(a_fp) == 0: continue

            a_fp = a_fp[0]
            # fault
            a_f = tuple(os.listdir(os.path.join(batchp, a_fp)))
            if len(a_f) == 0: continue

            a_f = a_f[0]
            fault_path = os.path.join(batchp, a_fp, a_f, 'fault.json')
            if os.path.exists(fault_path):
                with open(fault_path, "r", encoding="utf-8") as f:
                    fault = FaultInfo.from_dict(**json.load(f))
                    items.append(f"负责人:    {fault.worker: <30}    批次:    {bn: <30}")
        self.batchList.addItems(items)

    def _addBatch(self):
        if not self.currentUser:
            QMessageBox.warning(self, "错误", "请先登录")
            return

        batchName = self.batchEdit.text()
        success, msg = self.manager.addBatch(
            self.currentUser["role"],
            self.currentUser["id"],
            batchName
        )

        if success:
            self._refresh()
        else:
            QMessageBox.warning(self, "错误", msg)

    def _createUser(self):
        success, msg = self.manager.createUser(
            self.currentUser["role"],
            self.newUserEdit.text(),
            self.newPwdEdit.text(),
            Role(Role.c2e(self.roleCombo.currentText()))
        )

        if success:
            QMessageBox.information(self, "成功", msg)
        else:
            QMessageBox.warning(self, "错误", msg)


# ==========================
# 测试运行
# ==========================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = UserManagerWidget()
    widget.setWindowTitle("批次人员管理系统")
    widget.resize(500, 600)
    widget.show()
    sys.exit(app.exec_())
