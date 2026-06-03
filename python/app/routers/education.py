from fastapi import Depends, Request
from app.api.routes import SubmitAnswerRequest
from app.db.database import get_db
from app.services.learning_service import LearningService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

router = APIRouter(prefix="/education", tags=["education"])


@router.post("/submit")
async def submit_answer(
    req: SubmitAnswerRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = LearningService(request.app.state.orchestrator)
    return await service.submit_answer(db, req)

@router.get("/next-question/{user_id}")
async def get_next_question(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LearningService()

    return await service.get_next_question(
        db=db,
        user_id=user_id,
    )

@router.get("/progress/{user_id}")
async def get_progress(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LearningService()

    return await service.get_progress(
        db=db,
        user_id=user_id,
    )

@router.get("/reviews/{user_id}")
async def get_reviews(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = LearningService()

    return await service.get_due_reviews(
        db=db,
        user_id=user_id,
    )