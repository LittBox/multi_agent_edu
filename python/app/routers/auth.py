from fastapi import Depends, HTTPException, Request, APIRouter
from app.db.database import get_db
from app.services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    result = await auth_service.login(
        req.username,
        req.pwd
    )

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "code": 0,
        "message": "Login successful",
        "data": result
    }


@router.post("/register")
async def register(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        user = await auth_service.register_user(
            req.username,
            req.pwd
        )
        return {
            "code": 0,
            "message": "Registration successful",
            "data": {
                "user": {
                    "id": user.user_id,
                    "username": user.username,
                    "email": getattr(user, "email", ""),
                    "avatar": getattr(user, "avatar", None),
                    "role": getattr(user, "role", "user"),
                }
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get("/info/{user_id}")
async def get_user_info(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        user_info = await auth_service.get_user_info(user_id)
        return {
            "code": 0,
            "message": "User info retrieved successfully",
            "data": {
                "user": user_info
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    
@router.post("/change-password")
async def change_password(
    user_id: int,
    old_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        result = await auth_service.change_password(
            user_id,
            old_password,
            new_password
        )
        return {
            "code": 0,
            "message": "Password changed successfully",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    try:
        result = await auth_service.delete_user(user_id)
        return {
            "code": 0,
            "message": "User deleted successfully",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )