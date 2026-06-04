from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.schemas.learning import (
    HintRequest,
    SubmitAnswerRequest,
    TutorAskRequest,
    TutorMessageRequest,
)
from app.services.learning_service import LearningService
from app.services.report_service import ReportService

router = APIRouter(prefix="/education", tags=["education"])


def _learning_service(request: Request) -> LearningService:
    return LearningService(request.app.state.orchestrator)


@router.post("/submit")
async def submit_answer(
    req: SubmitAnswerRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, req.user_id)
    service = _learning_service(request)
    try:
        result = await service.submit_answer(db, req)
        return api_success(result, message="Answer submitted successfully")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/next-question/{user_id}")
async def get_next_question(
    user_id: int,
    knowledge_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = LearningService()
    question = await service.get_next_question(
        db=db,
        user_id=user_id,
        knowledge_id=knowledge_id,
    )
    if not question:
        return api_success(None, message="No question available")
    return api_success(question, message="Next question fetched successfully")


@router.get("/progress/{user_id}")
async def get_progress(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = LearningService()
    progress = await service.get_progress(db=db, user_id=user_id)
    return api_success(progress, message="Progress fetched successfully")


@router.get("/reviews/{user_id}")
async def get_reviews(
    user_id: int,
    due_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = LearningService()
    reviews = await service.get_due_reviews(
        db=db,
        user_id=user_id,
        due_only=due_only,
    )
    return api_success(reviews, message="Reviews fetched successfully")


@router.get("/answers/{user_id}")
async def get_answer_history(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = LearningService()
    history = await service.get_answer_history(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return api_success(history, message="Answer history fetched successfully")


@router.get("/report/{user_id}")
async def get_learning_report(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = ReportService(db)
    report = await service.get_learning_report(user_id)
    return api_success(report, message="Learning report fetched successfully")


@router.get("/knowledge-graph/{user_id}")
async def get_knowledge_graph(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, user_id)
    service = LearningService()
    graph = await service.get_knowledge_graph(db=db, user_id=user_id)
    return api_success(graph, message="Knowledge graph fetched successfully")


@router.post("/question")
async def tutor_ask(
    req: TutorAskRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, req.user_id)
    service = _learning_service(request)
    result = await service.tutor_ask(db, req)
    return api_success(result, message="Question processed successfully")


@router.post("/message")
async def tutor_message(
    req: TutorMessageRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, req.user_id)
    service = _learning_service(request)
    result = await service.tutor_message(db, req)
    return api_success(result, message="Message processed successfully")


@router.post("/hint")
async def request_hint(
    req: HintRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ensure_user_access(current_user, req.user_id)
    service = _learning_service(request)
    result = await service.request_hint(db, req)
    return api_success(result, message="Hint generated successfully")
