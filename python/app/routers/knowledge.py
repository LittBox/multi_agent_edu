from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.schemas.knowledge import CreateKnowledgePointRequest
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/repository/{user_id}")
async def get_knowledge_repository(
    user_id: int,
    q: str | None = Query(default=None, max_length=100),
    subject: str | None = Query(default=None, max_length=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = KnowledgeService(db)
    data = await service.get_repository(user_id, q=q, subject=subject)
    return api_success(data, message="Knowledge repository fetched successfully")


@router.get("/detail/{knowledge_id}")
async def get_knowledge_detail(
    knowledge_id: int,
    user_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = KnowledgeService(db)
    try:
        detail = await service.get_detail(knowledge_id, user_id)
        return api_success(detail, message="Knowledge detail fetched successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("")
async def create_knowledge_point(
    req: CreateKnowledgePointRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = KnowledgeService(db)
    try:
        created = await service.create_point(
            name=req.name,
            subject=req.subject,
            description=req.description,
            parent_id=req.parent_id,
            difficulty=req.difficulty,
        )
        return api_success(created, message="Knowledge point created successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{knowledge_id}")
async def delete_knowledge_point(
    knowledge_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = KnowledgeService(db)
    try:
        await service.delete_point(knowledge_id)
        return api_success(None, message="Knowledge point deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
