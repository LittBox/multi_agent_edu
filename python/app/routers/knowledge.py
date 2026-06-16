"""知识点与知识仓库路由。

对应前端 KnowledgeWarehouseView：
- GET /knowledge/repository/{user_id}：按 subject 分组展示知识卡片
- POST /knowledge/{knowledge_id}/join：加入个人知识仓库
- GET /knowledge/all-points：题库管理等页面用于选择知识点
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeCreateIn(BaseModel):
    """创建知识点。"""
    name: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=50)
    description: str | None = None
    parent_id: int | None = None
    difficulty: int = Field(default=1, ge=1)


class KnowledgeUpdateIn(BaseModel):
    """更新知识点。"""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    subject: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    parent_id: int | None = None
    difficulty: int | None = Field(default=None, ge=1)


def _require_staff(user: User) -> None:
    """知识点维护仅允许教师或管理员。"""
    if user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.get("/all-points")
async def get_all_points(q: str | None = Query(default=None), subject: str | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取知识点列表，供题库/后台选择知识点使用。"""
    data = await KnowledgeService(db).list_knowledge_points(q=q, subject=subject)
    return api_success(data, message="All points fetched successfully")


@router.get("/repository/{user_id}")
async def get_knowledge_repository(user_id: int, q: str | None = Query(default=None, max_length=100), subject: str | None = Query(default=None, max_length=50), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """知识仓库页面数据：知识点列表、学科筛选项、个人掌握状态。"""
    ensure_user_access(current_user, user_id)
    data = await KnowledgeService(db).get_repository(user_id, q=q, subject=subject)
    return api_success(data, message="Knowledge repository fetched successfully")


@router.get("/detail/{knowledge_id}")
async def get_knowledge_detail(knowledge_id: int, user_id: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """知识点详情，可选附带某个用户的学习状态。"""
    if user_id is not None:
        ensure_user_access(current_user, user_id)
    try:
        data = await KnowledgeService(db).get_detail(knowledge_id, user_id=user_id)
        return api_success(data, message="Knowledge detail fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{knowledge_id}/join")
async def join_knowledge_point(knowledge_id: int, user_id: int = Query(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生加入某知识点，创建 learner_state 与 review_schedule。"""
    ensure_user_access(current_user, user_id)
    try:
        data = await KnowledgeService(db).join_point(knowledge_id, user_id)
        return api_success(data, message="Knowledge point joined successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("")
async def create_knowledge_point(req: KnowledgeCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员创建知识点。"""
    _require_staff(current_user)
    try:
        data = await KnowledgeService(db).create_knowledge_point(**req.model_dump())
        return api_success(data, message="Knowledge point created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{knowledge_id}")
async def update_knowledge_point(knowledge_id: int, req: KnowledgeUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员更新知识点。"""
    _require_staff(current_user)
    try:
        data = await KnowledgeService(db).update_knowledge_point(knowledge_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Knowledge point updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{knowledge_id}")
async def delete_knowledge_point(knowledge_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员删除知识点。"""
    _require_staff(current_user)
    try:
        ok = await KnowledgeService(db).delete_knowledge_point(knowledge_id)
        return api_success(ok, message="Knowledge point deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
