from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password
from app.db.models.user import User

"""
用户数据访问对象
主要职责包括：
1. 创建用户
2. 根据ID查询用户
3. 根据用户名查询用户
4. 查询所有用户
5. 删除用户
6. 更新用户密码
7. 更新用户角色
8. 更新用户联系方式
"""
class UserDAO:

    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        pwd: str
    ) -> User:
        user = User(
            username=username,
            pwd=hash_password(pwd)
        )

        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        user_id: int
    ) -> User | None:

        result = await db.execute(
            select(User).where(
                User.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(
        db: AsyncSession,
        username: str
    ) -> User | None:

        result = await db.execute(
            select(User).where(
                User.username == username
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(User)
        )

        return result.scalars().all()

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: int
    ):

        user = await UserDAO.get_by_id(
            db,
            user_id
        )

        if not user:
            return False

        await db.delete(user)

        await db.commit()

        return True
    
    @staticmethod
    async def update_password(
        db: AsyncSession,
        user_id: int,
        new_pwd: str
    ) -> bool:

        user = await UserDAO.get_by_id(
            db,
            user_id
        )

        if not user:
            return False

        user.pwd = hash_password(new_pwd)

        await db.commit()

        return True

    @staticmethod
    async def update_role(
        db: AsyncSession,
        user_id: int,
        role: str,
    ) -> bool:
        user = await UserDAO.get_by_id(db, user_id)
        if not user:
            return False

        user.role = role
        await db.commit()
        return True

    @staticmethod
    async def update_contact_info(
        db: AsyncSession,
        user_id: int,
        email: str | None = None,
        phone: str | None = None,
    ) -> bool:
        user = await UserDAO.get_by_id(db, user_id)
        if not user:
            return False

        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone

        await db.commit()
        return True
