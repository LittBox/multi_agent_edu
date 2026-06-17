"""学习与题库路由。

本文件同时服务两个场景：
1. 学生练习：获取题目、提交答案、查看进度/复习/报告。
2. 教师题库维护：创建、更新、删除题目。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.dependencies.user_access import ensure_user_access
from app.schemas.api_response import api_success
from app.schemas.learning import ExplanationRequest, HintRequest, SubmitAnswerRequest, TutorAskRequest, TutorMessageRequest
from app.services.learning_service import LearningService
from app.services.question_service import QuestionService
from app.services.report_service import ReportService
from app.dependencies.learning import get_learning_service

router = APIRouter(prefix="/education", tags=["education"])


class QuestionCreateIn(BaseModel):
    """创建题目请求体。"""
    knowledge_id: int | None = None
    question_type: str = Field(min_length=1, max_length=30)
    stem: str = Field(min_length=1)
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    answer: str = Field(min_length=1)
    explanation: str | None = None
    difficulty: int = Field(default=1, ge=1)
    image_url: str | None = None


class QuestionUpdateIn(BaseModel):
    """更新题目请求体。"""
    knowledge_id: int | None = None
    question_type: str | None = None
    stem: str | None = None
    option_a: str | None = None
    option_b: str | None = None
    option_c: str | None = None
    option_d: str | None = None
    answer: str | None = None
    explanation: str | None = None
    difficulty: int | None = Field(default=None, ge=1)
    image_url: str | None = None




def _require_staff(user: User) -> None:
    if user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.get("/questions")
async def list_questions(user_id: int | None = Query(default=None), knowledge_id: int | None = Query(default=None), question_type: str | None = Query(default=None), difficulty: int | None = Query(default=None), include_answer: bool = Query(default=False), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查询题目列表。学生端默认不返回正确答案；教师端可 include_answer=true。"""
    if user_id is not None:
        ensure_user_access(current_user, user_id)
    data = await QuestionService(db).list_questions(
        knowledge_id=knowledge_id,
        question_type=question_type,
        difficulty=difficulty,
        include_answer=include_answer and current_user.role in {"admin", "teacher"},
    )
    return api_success(data, message="Questions fetched successfully")


@router.post("/questions")
async def create_question(req: QuestionCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员创建题目。"""
    _require_staff(current_user)
    try:
        data = await QuestionService(db).create_question(**req.model_dump())
        return api_success(data, message="Question created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/questions/{question_id}")
async def get_question(question_id: int, include_answer: bool = Query(default=False), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查询单个题目。"""
    try:
        data = await QuestionService(db).get_question(question_id, include_answer=include_answer and current_user.role in {"admin", "teacher"})
        return api_success(data, message="Question fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/questions/{question_id}")
async def update_question(question_id: int, req: QuestionUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员更新题目。"""
    _require_staff(current_user)
    try:
        data = await QuestionService(db).update_question(question_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Question updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员删除题目。"""
    _require_staff(current_user)
    try:
        ok = await QuestionService(db).delete_question(question_id)
        return api_success(ok, message="Question deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/submit")
async def submit_answer(
    req: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    try:
        data = await service.submit_answer(db, req)
        return api_success(data, message="Answer submitted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/next-question/{user_id}")
async def get_next_question(
    user_id: int,
    knowledge_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """按知识点、复习计划和薄弱点获取下一题。"""
    ensure_user_access(current_user, user_id)
    data = await service.get_next_question(
        db=db,
        user_id=user_id,
        knowledge_id=knowledge_id,
    )
    return api_success(
        data,
        message="Next question fetched successfully" if data else "No question available",
    )


@router.get("/progress/{user_id}")
async def get_progress(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """获取学习进度。"""
    ensure_user_access(current_user, user_id)
    data = await service.get_progress(db=db, user_id=user_id)
    return api_success(data, message="Progress fetched successfully")


@router.get("/reviews/{user_id}")
async def get_reviews(
    user_id: int,
    due_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """获取复习计划。"""
    ensure_user_access(current_user, user_id)
    data = await service.get_due_reviews(
        db=db,
        user_id=user_id,
        due_only=due_only,
    )
    return api_success(data, message="Reviews fetched successfully")


@router.get("/answers/{user_id}")
async def get_answer_history(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """获取答题历史。"""
    ensure_user_access(current_user, user_id)
    data = await service.get_answer_history(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return api_success(data, message="Answer history fetched successfully")


@router.get("/report/{user_id}")
async def get_learning_report(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """获取学习报告。"""
    ensure_user_access(current_user, user_id)
    data = await ReportService(db).get_learning_report(user_id)
    return api_success(data, message="Learning report fetched successfully")


@router.post("/question")
async def tutor_ask(
    req: TutorAskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """智能辅导：提问。"""
    ensure_user_access(current_user, req.user_id)
    data = await service.tutor_ask(db, req)
    return api_success(data, message="Question processed successfully")


@router.post("/message")
async def tutor_message(
    req: TutorMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """智能辅导：继续对话。"""
    ensure_user_access(current_user, req.user_id)
    data = await service.tutor_message(db, req)
    return api_success(data, message="Message processed successfully")


@router.post("/hint")
async def request_hint(
    req: HintRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """智能辅导：请求提示。"""
    ensure_user_access(current_user, req.user_id)
    data = await service.request_hint(db, req)
    return api_success(data, message="Hint generated successfully")


@router.post("/explain")
async def explain_answer(
    req: ExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LearningService = Depends(get_learning_service),
):
    """智能辅导：解释答案。"""
    ensure_user_access(current_user, req.user_id)
    data = await service.explain_answer(db, req)
    return api_success(data, message="Explanation generated successfully")