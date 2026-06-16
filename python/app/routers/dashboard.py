"""学习仪表盘路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取首页摘要和学习路径。"""
    ensure_user_access(current_user, user_id)
    service = DashboardService(db)
    summary = await service.get_dashboard_summary(user_id)
    path = await service.get_learning_path(user_id)
    return api_success({"summary": summary, "learning_path": path}, message="Dashboard fetched successfully")


@router.get("/knowledge-cards/{user_id}")
async def get_knowledge_cards(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取知识掌握卡片。"""
    ensure_user_access(current_user, user_id)
    data = await DashboardService(db).get_knowledge_cards(user_id)
    return api_success(data, message="Knowledge cards fetched successfully")
