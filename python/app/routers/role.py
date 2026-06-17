
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.services.role_service import RoleService, StudentRoleUpdatePayload
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/students/me")
async def get_my_student_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await RoleService(db).get_my_student_info(current_user.user_id)
        return api_success(data, "Student info loaded successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/students/me")
async def update_my_student_info(
    payload: StudentRoleUpdatePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await RoleService(db).update_my_student_info(
            current_user.user_id,
            payload,
        )
        return api_success(data, "Student info updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))