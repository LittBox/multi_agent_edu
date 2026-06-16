"""考试路由。

对应前端 ExamView：
- GET /exams：上方“已发布考试/考试列表”卡片
- POST /exams：教师创建考试
- POST /exams/{exam_id}/questions：教师组卷
- GET /exams/{exam_id}/start：学生进入考试
- POST /exams/{exam_id}/submit：学生提交试卷
- GET /exams/submissions/me：学生下方“我的考试记录”
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success
from app.services.exam_service import ExamService

router = APIRouter(prefix="/exams", tags=["exams"])


class ExamCreateIn(BaseModel):
    """创建考试请求体。teacher_id 由当前登录教师档案确定。"""
    title: str = Field(min_length=1, max_length=200)
    course_id: int
    duration_minutes: int = Field(default=60, gt=0)
    exam_type: str = "quiz"
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str = "published"


class ExamUpdateIn(BaseModel):
    """更新考试请求体。"""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    course_id: int | None = None
    teacher_id: int | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    exam_type: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None


class ExamQuestionIn(BaseModel):
    """向试卷中加入题目。"""
    question_id: int
    score: float = Field(default=10, gt=0)
    sort_order: int = 0


class ExamSubmitIn(BaseModel):
    """学生提交答案。前端传入 {question_id: answer}。"""
    answers: dict[str, Any] | list[dict]


class ExamReviewIn(BaseModel):
    """教师复核或人工调整成绩。"""
    total_score: float = Field(ge=0)
    teacher_comment: str | None = None


def _require_staff(user: User) -> None:
    if user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")


def _require_student(user: User) -> None:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this resource")


@router.get("")
async def list_exams(status: str | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """考试列表。学生端通常只展示已发布考试，具体过滤由前端或 status 参数控制。"""
    service = ExamService(db)
    data = await service.list_exams(status=status)
    if current_user.role == "student" and status is None:
        data = [item for item in data if item.get("status") in {"published", "active", "ongoing"}]
    return api_success(data, message="Exams fetched successfully")


@router.post("")
async def create_exam(req: ExamCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员创建考试。"""
    _require_staff(current_user)
    try:
        data = await ExamService(db).create_exam_by_user(
            user_id=current_user.user_id,
            title=req.title,
            course_id=req.course_id,
            duration_minutes=req.duration_minutes,
            exam_type=req.exam_type,
            start_time=req.start_time,
            end_time=req.end_time,
            status=req.status,
        )
        return api_success(data, message="Exam created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{exam_id}")
async def get_exam(exam_id: int, include_questions: bool = Query(default=True), include_answer: bool = Query(default=False), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查看考试详情。教师可通过 include_answer 查看答案。"""
    try:
        data = await ExamService(db).get_exam(exam_id, include_questions=include_questions, include_answer=include_answer and current_user.role in {"admin", "teacher"})
        return api_success(data, message="Exam fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{exam_id}")
async def update_exam(exam_id: int, req: ExamUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新考试基础信息。"""
    _require_staff(current_user)
    try:
        data = await ExamService(db).update_exam(exam_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Exam updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/{exam_id}")
async def delete_exam(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """软删除考试。"""
    _require_staff(current_user)
    try:
        ok = await ExamService(db).delete_exam(exam_id)
        return api_success(ok, message="Exam deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{exam_id}/questions")
async def add_exam_question(exam_id: int, req: ExamQuestionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师组卷：把题库题目加入考试。"""
    _require_staff(current_user)
    try:
        data = await ExamService(db).add_question(exam_id, req.question_id, score=req.score, sort_order=req.sort_order)
        return api_success(data, message="Exam question added successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{exam_id}/questions")
async def list_exam_questions(exam_id: int, include_answer: bool = Query(default=False), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查看试卷题目。学生端不返回正确答案。"""
    try:
        data = await ExamService(db).list_exam_questions(exam_id, include_answer=include_answer and current_user.role in {"admin", "teacher"})
        return api_success(data, message="Exam questions fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{exam_id}/questions/{question_id}")
async def remove_exam_question(exam_id: int, question_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """从试卷中移除题目。"""
    _require_staff(current_user)
    try:
        ok = await ExamService(db).remove_question(exam_id, question_id)
        return api_success(ok, message="Exam question removed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/{exam_id}/start")
async def start_exam(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生进入考试，返回不含正确答案的试卷。"""
    _require_student(current_user)
    try:
        data = await ExamService(db).start_exam(exam_id, user_id=current_user.user_id)
        return api_success(data, message="Exam started successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{exam_id}/submit")
async def submit_exam(exam_id: int, req: ExamSubmitIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生提交试卷，service 层会自动计算客观题分数。"""
    _require_student(current_user)
    try:
        data = await ExamService(db).submit_exam(exam_id, current_user.user_id, req.answers)
        return api_success(data, message="Exam submitted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/submissions/me")
async def my_exam_submissions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生查看自己的考试提交记录。"""
    _require_student(current_user)
    try:
        data = await ExamService(db).my_submissions(current_user.user_id)
        return api_success(data, message="Exam submissions fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/submissions/{exam_submit_id}/review")
async def review_exam(exam_submit_id: int, req: ExamReviewIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员复核考试成绩。"""
    _require_staff(current_user)
    try:
        data = await ExamService(db).grade_submit(exam_submit_id, req.total_score, req.teacher_comment)
        return api_success(data, message="Exam reviewed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
