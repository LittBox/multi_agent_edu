from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password
from app.db.models.user import User

"""
用户 DAO。
对应模型 users：user_id、username、pwd、role、email、avatar、status、created_at、updated_at。
注意：pwd 是密文存储；DAO 默认会对新密码调用 hash_password。
"""

class UserDAO:
    @staticmethod
    async def create_user(db: AsyncSession, username: str, pwd: str, role: str = "student",
                          email: str | None = None, avatar: str | None = None,
                          status: str = "active", pwd_already_hashed: bool = False) -> User:
        user = User(username=username, pwd=pwd if pwd_already_hashed else hash_password(pwd),
                    role=role, email=email, avatar=avatar, status=status)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int, include_deleted: bool = False) -> User | None:
        conditions = [User.user_id == user_id]
        if not include_deleted:
            conditions.append(User.status != "deleted")
        result = await db.execute(select(User).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str, include_deleted: bool = False) -> User | None:
        conditions = [User.username == username]
        if not include_deleted:
            conditions.append(User.status != "deleted")
        result = await db.execute(select(User).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession, role: str | None = None, status: str | None = None,
                      include_deleted: bool = False) -> list[User]:
        conditions = []
        if role is not None:
            conditions.append(User.role == role)
        if status is not None:
            conditions.append(User.status == status)
        elif not include_deleted:
            conditions.append(User.status != "deleted")
        stmt = select(User)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await db.execute(stmt.order_by(User.user_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
        user = await UserDAO.get_by_username(db, username)
        if not user or user.status != "active":
            return None
        return user if verify_password(password, user.pwd) else None

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, username: str | None = None,
                          role: str | None = None, email: str | None = None,
                          avatar: str | None = None, status: str | None = None) -> User | None:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            return None
        if username is not None:
            user.username = username
        if role is not None:
            user.role = role
        if email is not None:
            user.email = email
        if avatar is not None:
            user.avatar = avatar
        if status is not None:
            user.status = status
        user.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_password(db: AsyncSession, user_id: int, new_pwd: str,
                              pwd_already_hashed: bool = False) -> bool:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            return False
        user.pwd = new_pwd if pwd_already_hashed else hash_password(new_pwd)
        user.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def update_role(db: AsyncSession, user_id: int, role: str) -> bool:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            return False
        user.role = role
        user.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def update_status(db: AsyncSession, user_id: int, status: str) -> bool:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            return False
        user.status = status
        user.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def update_contact_info(db: AsyncSession, user_id: int,
                                  email: str | None = None, avatar: str | None = None) -> bool:
        # 当前 User 模型只有 email/avatar，没有 phone 字段。
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            return False
        if email is not None:
            user.email = email
        if avatar is not None:
            user.avatar = avatar
        user.updated_at = datetime.now(UTC)
        await db.commit()
        return True

    @staticmethod
    async def soft_delete(db: AsyncSession, user_id: int) -> bool:
        return await UserDAO.update_status(db, user_id, "deleted")

    @staticmethod
    async def hard_delete(db: AsyncSession, user_id: int) -> bool:
        user = await UserDAO.get_by_id(db, user_id, include_deleted=True)
        if not user:
            return False
        await db.delete(user)
        await db.commit()
        return True
