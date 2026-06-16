"""认证服务。

面向 router 的核心能力：登录、注册、当前用户信息、修改密码、更新个人基础信息。
注意：用户密码字段 pwd 使用密文存储，所有返回数据都不会暴露 pwd。
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.dao.userDao import UserDAO
from app.dao.UserRoleDAO import UserRoleDAO
from app.services._helpers import user_to_dict


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, username: str, password: str, role: str | None = None) -> dict | None:
        """登录。

        前端通常传入：username、password、role。role 可为空；不为空时会同时校验
        users.role 和 user_roles 关联角色，避免学生用教师入口登录。
        """
        user = await UserDAO.get_by_username(self.db, username)
        if not user or not verify_password(password, user.pwd):
            return None
        if user.status != "active":
            raise ValueError("User is not active")

        actual_role = user.role
        user_role = await UserRoleDAO.get_user_role(self.db, user.user_id)
        if user_role:
            role_name = await UserRoleDAO.get_role_name(self.db, user_role.role_id)
            if role_name:
                actual_role = role_name

        if role and actual_role != role:
            raise ValueError("User role does not match")

        token = create_access_token({
            "sub": str(user.user_id),
            "username": user.username,
            "role": actual_role,
        })
        data = user_to_dict(user)
        data["role"] = actual_role
        return {"token": token, "user": data}

    async def authenticate_user(self, username: str, password: str):
        user = await UserDAO.get_by_username(self.db, username)
        if user and user.status == "active" and verify_password(password, user.pwd):
            return user
        return None

    async def register_user(self, username: str, password: str, role: str = "student",
                            email: str | None = None, avatar: str | None = None):
        if role not in {"admin", "teacher", "student"}:
            raise ValueError("Invalid role")
        existing = await UserDAO.get_by_username(self.db, username, include_deleted=True)
        if existing:
            raise ValueError("Username already exists")
        user = await UserDAO.create_user(self.db, username=username, pwd=password, role=role, email=email, avatar=avatar)
        await UserRoleDAO.assign_role_to_user(self.db, user.user_id, role)
        return user

    async def get_user_info(self, user_id: int) -> dict:
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        return user_to_dict(user)

    async def update_profile(self, user_id: int, email: str | None = None,
                             avatar: str | None = None, username: str | None = None) -> dict:
        user = await UserDAO.update_user(self.db, user_id, username=username, email=email, avatar=avatar)
        if not user:
            raise ValueError("User not found")
        return user_to_dict(user)

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(old_password, user.pwd):
            raise ValueError("Old password is incorrect")
        return await UserDAO.update_password(self.db, user_id, new_password, pwd_already_hashed=False)

    async def update_status(self, user_id: int, status: str) -> bool:
        if status not in {"active", "inactive", "deleted"}:
            raise ValueError("Invalid status")
        ok = await UserDAO.update_status(self.db, user_id, status)
        if not ok:
            raise ValueError("User not found")
        return ok
