from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.dao.userDao import UserDAO
from app.schemas.user_response import user_to_dict

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
       
    async def login(self, username: str, password: str):
        user = await UserDAO.get_by_username(self.db, username)

        if not user or not verify_password(password, user.pwd):
            return None

        token = create_access_token({
            "sub": str(user.user_id),
            "username": user.username,
        })

        return {
            "token": token,
            "user": user_to_dict(user),
        }   

    async def authenticate_user(self, username: str, password: str):
        user = await UserDAO.get_by_username(self.db, username)
        if user and verify_password(password, user.pwd):
            return user
        return None
    
    async def register_user(self, username: str, password: str):
        existing_user = await UserDAO.get_by_username(self.db, username)
        
        if existing_user:
            raise ValueError("Username already exists")
        new_user = await UserDAO.create_user(self.db, username, password)  # 已在Dao层使用哈希密码
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
            "username": user.username
        }
 