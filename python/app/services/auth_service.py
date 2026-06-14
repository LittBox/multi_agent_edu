from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.dao.userDao import UserDAO
from app.dao.UserRoleDAO import UserRoleDAO
from app.schemas.user_response import user_to_dict


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, username: str, password: str, role: str | None = None):
        user = await UserDAO.get_by_username(self.db, username)

        if not user or not verify_password(password, user.pwd):
            return None

        if role:
            user_role = await UserRoleDAO.get_user_role(self.db, user.user_id)
            if not user_role:
                raise ValueError("User role does not match")

            #和用户角色表进行比对，确保用户的角色与登录请求中的角色一致
            role_name = await UserRoleDAO.get_role_name(self.db, user_role.role_id)
            if role_name != role:
                raise ValueError("User role does not match")

        token = create_access_token(
            {
                "sub": str(user.user_id),
                "username": user.username,
                "role": role,
            }
        )

        return {
            "token": token,
            "user": user_to_dict(user),
        }

    async def authenticate_user(self, username: str, password: str):
        user = await UserDAO.get_by_username(self.db, username)
        if user and verify_password(password, user.pwd):
            return user
        return None

    async def register_user(self, username: str, password: str, role: str):
        existing_user = await UserDAO.get_by_username(self.db, username)

        if existing_user:
            raise ValueError("Username already exists")

        new_user = await UserDAO.create_user(self.db, username, password)
        await UserRoleDAO.assign_role_to_user(self.db, new_user.user_id, role)
        await UserDAO.update_role(self.db, new_user.user_id, role)
        return new_user

    async def get_user_info(self, user_id: int):
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        return user_to_dict(user)

    async def change_password(self, user_id: int, old_password: str, new_password: str):
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(old_password, user.pwd):
            raise ValueError("Old password is incorrect")
        if old_password == new_password:
            raise ValueError("New password cannot be the same as the old password")
        await UserDAO.update_password(self.db, user_id, new_password)
        return {"message": "Password changed successfully"}

    async def delete_user(self, user_id: int):
        user = await UserDAO.get_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        await UserDAO.delete_user(self.db, user_id)
        return {
            "message": "User deleted successfully",
            "username": user.username,
        }
