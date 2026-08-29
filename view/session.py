""" 登录会话 (UI 重构新增): 保存当前登录用户, 驱动导航/功能权限可见性 """
from core.database import Role


class _Session:
    def __init__(self):
        self.user = None  # UserManager.login 成功返回的 dict: {id, username, role}

    def set_user(self, user):
        self.user = user

    def logout(self):
        self.user = None

    @property
    def role(self):
        return self.user['role'] if self.user else None

    @property
    def username(self):
        return self.user['username'] if self.user else None

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_manager(self):
        return self.role in (Role.ADMIN, Role.MANAGER)

    @property
    def is_worker_only(self):
        return self.role == Role.WORKER


Session = _Session()
