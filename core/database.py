import sys
import sqlite3
import hashlib
import os
import json
import datetime
from enum import Enum
from threading import Lock

from .const import Path


# ==========================
# 枚举定义
# ==========================

class Role(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    WORKER = "worker"

    def e2c(self):
        if self == Role.ADMIN:
            return "管理员"
        elif self == Role.MANAGER:
            return "经理"
        elif self == Role.WORKER:
            return "工人"
    @classmethod
    def c2e(self,c):
        if c == "管理员":
            return Role.ADMIN.value
        elif c == "经理":
            return Role.MANAGER.value
        elif c == "工人":
            return Role.WORKER.value
        raise NotImplementedError

class Permission(Enum):
    CREATE_USER = "createUser"
    ADD_BATCH = "addBatch"
    VIEW_ALL = "viewAll"


# ==========================
# 单例用户管理类
# ==========================

class UserManager:
    _instance = None
    _lock = Lock()
    # 固定在程序根目录的 config 下, 不依赖当前工作目录
    dbName = os.path.join(Path.CONFIG_DIR, "users.db")

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._initDb()
        self._ensureDefaultAdmin()

    def _initDb(self):
        if not os.path.exists(self.dbName):
            os.makedirs(os.path.dirname(self.dbName),exist_ok=True)
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            passwordHash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL,
            strList TEXT DEFAULT '[]',
            createdAt TEXT NOT NULL
        )
        """)

        # 旧库迁移: 补充 lastLogin / enabled 列 (已存在则忽略)
        for ddl in ("ALTER TABLE users ADD COLUMN lastLogin TEXT",
                    "ALTER TABLE users ADD COLUMN enabled INTEGER DEFAULT 1"):
            try:
                cursor.execute(ddl)
            except sqlite3.OperationalError:
                pass

        conn.commit()
        conn.close()

    def _ensureDefaultAdmin(self):
        if not self._userExists("admin"):
            pwdHash, salt = self._hashPassword("admin123")
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, passwordHash, salt, role, createdAt)
            VALUES (?, ?, ?, ?, ?)
            """, (
                "admin",
                pwdHash,
                salt,
                Role.ADMIN.value,
                datetime.datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()

    def _userExists(self, username):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    # -----------------------
    # 密码
    # -----------------------

    def _hashPassword(self, password, salt=None):
        if salt is None:
            salt = os.urandom(16)

        pwdHash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            100000
        )
        return pwdHash.hex(), salt.hex()

    def _verifyPassword(self, storedHash, storedSalt, inputPassword):
        salt = bytes.fromhex(storedSalt)
        inputHash, _ = self._hashPassword(inputPassword, salt)
        return inputHash == storedHash

    # -----------------------
    # 权限
    # -----------------------

    def _rolePermissions(self):
        return {
            Role.ADMIN: {Permission.CREATE_USER, Permission.ADD_BATCH, Permission.VIEW_ALL},
            Role.MANAGER: {Permission.ADD_BATCH, Permission.VIEW_ALL},
            Role.WORKER: {Permission.ADD_BATCH}
        }

    def _hasPermission(self, role, permission):
        return permission in self._rolePermissions().get(role, set())

    # -----------------------
    # 登录
    # -----------------------

    def login(self, username, password):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, passwordHash, salt, role, enabled FROM users WHERE username = ?
        """, (username,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return False, "User not found"

        userId, pwdHash, salt, roleStr, enabled = user
        if not self._verifyPassword(pwdHash, salt, password):
            conn.close()
            return False, "Wrong password"
        if enabled is not None and not enabled:
            conn.close()
            return False, "User disabled"
        cursor.execute("UPDATE users SET lastLogin = ? WHERE id = ?",
                       (datetime.datetime.now().isoformat(), userId))
        conn.commit()
        conn.close()
        return True, {
            "id": userId,
            "username": username,
            "role": Role(roleStr)
        }

    # -----------------------
    # 创建用户
    # -----------------------

    def createUser(self, operatorRole, username, password, role):
        if not self._hasPermission(operatorRole, Permission.CREATE_USER):
            return False, "Permission denied"

        pwdHash, salt = self._hashPassword(password)

        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO users (username, passwordHash, salt, role, createdAt)
            VALUES (?, ?, ?, ?, ?)
            """, (
                username,
                pwdHash,
                salt,
                role.value,
                datetime.datetime.now().isoformat()
            ))
            conn.commit()
            return True, "User created"
        except sqlite3.IntegrityError:
            return False, "Username exists"
        finally:
            conn.close()

    # -----------------------
    # 添加批次
    # -----------------------

    def addBatch(self, operatorRole, userId, batchName):
        if not self._hasPermission(operatorRole, Permission.ADD_BATCH):
            return False, "Permission denied"

        user = self.getUser(userId)
        if not user:
            return False, "User not found"

        strList = user["strList"]
        strList.append(batchName)

        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET strList = ? WHERE id = ?
        """, (json.dumps(strList), userId))
        conn.commit()
        conn.close()

        return True, "Batch added"

    def findUserByBatch(self, batchName):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("SELECT username, strList FROM users")
        users = cursor.fetchall()
        conn.close()

        result = []
        for username, strList in users:
            if batchName in json.loads(strList):
                result.append(username)
        return result

    def getUser(self, userId):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, username, role, strList FROM users WHERE id = ?
        """, (userId,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return None

        return {
            "id": user[0],
            "username": user[1],
            "role": Role(user[2]),
            "strList": json.loads(user[3])
        }

    def getAllUsernames(self):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        names = [u[0] for u in cursor.fetchall()]
        conn.close()
        return names

    # -----------------------
    # 用户管理 (UI 重构新增)
    # -----------------------

    def listUsers(self):
        """ 全部用户信息列表 (用户管理页) """
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, username, role, createdAt, lastLogin, enabled FROM users ORDER BY id
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0],
            "username": r[1],
            "role": Role(r[2]),
            "createdAt": r[3],
            "lastLogin": r[4],
            "enabled": bool(r[5]) if r[5] is not None else True,
        } for r in rows]

    def resetPassword(self, operatorRole, username, newPassword):
        """ 重置指定用户密码 (需 CREATE_USER 权限) """
        if not self._hasPermission(operatorRole, Permission.CREATE_USER):
            return False, "Permission denied"
        pwdHash, salt = self._hashPassword(newPassword)
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET passwordHash = ?, salt = ? WHERE username = ?",
                       (pwdHash, salt, username))
        changed = cursor.rowcount
        conn.commit()
        conn.close()
        if changed == 0:
            return False, "User not found"
        return True, "Password reset"

    def setUserEnabled(self, operatorRole, username, enabled: bool):
        """ 启用/禁用用户 (需 CREATE_USER 权限; 不允许禁用管理员以防锁死系统) """
        if not self._hasPermission(operatorRole, Permission.CREATE_USER):
            return False, "Permission denied"
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row is None:
            conn.close()
            return False, "User not found"
        if not enabled and row[0] == Role.ADMIN.value:
            conn.close()
            return False, "Cannot disable admin"
        cursor.execute("UPDATE users SET enabled = ? WHERE username = ?",
                       (1 if enabled else 0, username))
        conn.commit()
        conn.close()
        return True, "User enabled" if enabled else "User disabled"

    def getUsersByBatch(self, batchName):
        conn = sqlite3.connect(self.dbName)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, strList FROM users
            WHERE strList LIKE ?
        """, (f'%"{batchName}"%',))

        users = cursor.fetchall()
        conn.close()

        result = []

        for username, strListStr in users:
            try:
                batchList = json.loads(strListStr)
            except json.JSONDecodeError as e:
                # 打日志，而不是静默忽略
                print(f"[ERROR] JSON decode failed for user {username}: {e}")
                continue

            if batchName in batchList:
                result.append(username)

        return result