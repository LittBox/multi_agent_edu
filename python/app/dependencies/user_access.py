from fastapi import Depends, HTTPException

from app.db.models.user import User
from app.dependencies.auth import get_current_user


async def get_current_user_id(
    current_user: User = Depends(get_current_user),
) -> int:
    return current_user.user_id


def ensure_user_access(current_user: User, user_id: int) -> None:
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to access this user's data",
        )
