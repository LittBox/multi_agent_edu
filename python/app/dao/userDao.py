from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password
from app.db.models.user import User


class UserDAO:

    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        pwd: str
    ) -> User:
        print("pwd:", pwd)
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