from datetime import datetime, UTC
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.exam import Exam, ExamQuestion, ExamSubmit
from app.db.models.question import Question
from app.db.models.student import Student
from app.db.models.teacher import Teacher
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success

router = APIRouter(prefix="/exams", tags=["exams"])


class ExamIn(BaseModel):
    title: str
    course_id: int
    duration_minutes: int = 60
    exam_type: str = "quiz"
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str = "published"


class ExamQuestionIn(BaseModel):
    question_id: int
    score: float = 10
    sort_order: int = 0


class ExamSubmitIn(BaseModel):
    answers: dict[str, Any]


class ExamReviewIn(BaseModel):
    total_score: float | None = None
    teacher_comment: str | None = None


async def _teacher_id(db: AsyncSession, user: User) -> int:
    teacher = (await db.execute(select(Teacher).where(Teacher.user_id == user.user_id))).scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    return teacher.teacher_id


async def _student_id(db: AsyncSession, user: User) -> int:
    student = (await db.execute(select(Student).where(Student.user_id == user.user_id))).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student.student_id


def _exam_dict(exam: Exam) -> dict:
    return {
        "exam_id": exam.exam_id,
        "title": exam.title,
        "course_id": exam.course_id,
        "teacher_id": exam.teacher_id,
        "duration_minutes": exam.duration_minutes,
        "exam_type": exam.exam_type,
        "start_time": exam.start_time,
        "end_time": exam.end_time,
        "status": exam.status,
    }


def _question_dict(item: ExamQuestion) -> dict:
    q = item.question
    return {
        "exam_question_id": item.exam_question_id,
        "exam_id": item.exam_id,
        "question_id": item.question_id,
        "score": item.score,
        "sort_order": item.sort_order,
        "stem": q.stem if q else None,
        "question_type": q.question_type if q else None,
        "option_a": q.option_a if q else None,
        "option_b": q.option_b if q else None,
        "option_c": q.option_c if q else None,
        "option_d": q.option_d if q else None,
    }


def _submit_dict(submit: ExamSubmit) -> dict:
    return {
        "exam_submit_id": submit.exam_submit_id,
        "exam_id": submit.exam_id,
        "student_id": submit.student_id,
        "submit_time": submit.submit_time,
        "total_score": submit.total_score,
        "teacher_comment": submit.teacher_comment,
        "answers_json": submit.answers_json,
    }


@router.get("")
async def list_exams(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Exam).where(Exam.is_deleted == 0).order_by(Exam.created_at.desc())
    if current_user.role == "teacher":
        stmt = stmt.where(Exam.teacher_id == await _teacher_id(db, current_user))
    elif current_user.role == "student":
        stmt = stmt.where(Exam.status.in_(["published", "active"]))
    exams = (await db.execute(stmt)).scalars().all()
    return api_success([_exam_dict(exam) for exam in exams], message="Exams fetched successfully")


@router.post("")
async def create_exam(req: ExamIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")
    teacher_id = await _teacher_id(db, current_user)
    exam = Exam(**req.model_dump(), teacher_id=teacher_id)
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return api_success(_exam_dict(exam), message="Exam created successfully")


@router.get("/{exam_id}")
async def get_exam(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam or exam.is_deleted:
        raise HTTPException(status_code=404, detail="Exam not found")
    questions = (await db.execute(select(ExamQuestion).where(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order))).scalars().all()
    data = _exam_dict(exam)
    data["questions"] = [_question_dict(item) for item in questions]
    return api_success(data, message="Exam fetched successfully")


@router.delete("/{exam_id}")
async def delete_exam(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam or exam.is_deleted:
        raise HTTPException(status_code=404, detail="Exam not found")
    if current_user.role == "teacher" and exam.teacher_id != await _teacher_id(db, current_user):
        raise HTTPException(status_code=403, detail="Permission denied")
    exam.is_deleted = 1
    await db.commit()
    return api_success({"exam_id": exam_id}, message="Exam deleted successfully")


@router.post("/{exam_id}/questions")
async def add_exam_question(exam_id: int, req: ExamQuestionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")
    if not await db.get(Exam, exam_id):
        raise HTTPException(status_code=404, detail="Exam not found")
    if not await db.get(Question, req.question_id):
        raise HTTPException(status_code=404, detail="Question not found")
    item = ExamQuestion(exam_id=exam_id, **req.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item, ["question"])
    return api_success(_question_dict(item), message="Exam question added successfully")


@router.get("/{exam_id}/start")
async def start_exam(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    exam = await db.get(Exam, exam_id)
    if not exam or exam.is_deleted:
        raise HTTPException(status_code=404, detail="Exam not found")
    questions = (await db.execute(select(ExamQuestion).where(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order))).scalars().all()
    data = _exam_dict(exam)
    data["server_time"] = datetime.now(UTC)
    data["questions"] = [_question_dict(item) for item in questions]
    return api_success(data, message="Exam started successfully")


@router.post("/{exam_id}/submit")
async def submit_exam(exam_id: int, req: ExamSubmitIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    student_id = await _student_id(db, current_user)
    exam = await db.get(Exam, exam_id)
    if not exam or exam.is_deleted:
        raise HTTPException(status_code=404, detail="Exam not found")
    exam_questions = (await db.execute(select(ExamQuestion).where(ExamQuestion.exam_id == exam_id))).scalars().all()
    total_score = 0.0
    for item in exam_questions:
        question = await db.get(Question, item.question_id)
        answer = str(req.answers.get(str(item.question_id), "")).strip()
        if question and answer and answer.lower() == question.answer.strip().lower():
            total_score += item.score
    existing = (await db.execute(select(ExamSubmit).where(ExamSubmit.exam_id == exam_id, ExamSubmit.student_id == student_id))).scalar_one_or_none()
    if existing:
        existing.answers_json = req.answers
        existing.total_score = total_score
        existing.submit_time = datetime.now(UTC)
        submit = existing
    else:
        submit = ExamSubmit(exam_id=exam_id, student_id=student_id, answers_json=req.answers, total_score=total_score)
        db.add(submit)
    await db.commit()
    await db.refresh(submit)
    return api_success(_submit_dict(submit), message="Exam submitted successfully")


@router.get("/submissions/me")
async def my_exam_submissions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    student_id = await _student_id(db, current_user)
    submissions = (await db.execute(select(ExamSubmit).where(ExamSubmit.student_id == student_id).order_by(ExamSubmit.submit_time.desc()))).scalars().all()
    return api_success([_submit_dict(item) for item in submissions], message="Exam submissions fetched successfully")


@router.get("/{exam_id}/submissions")
async def exam_submissions(exam_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")
    submissions = (await db.execute(select(ExamSubmit).where(ExamSubmit.exam_id == exam_id).order_by(ExamSubmit.submit_time.desc()))).scalars().all()
    return api_success([_submit_dict(item) for item in submissions], message="Exam submissions fetched successfully")


@router.put("/submissions/{exam_submit_id}/review")
async def review_exam(exam_submit_id: int, req: ExamReviewIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")
    submit = await db.get(ExamSubmit, exam_submit_id)
    if not submit:
        raise HTTPException(status_code=404, detail="Exam submission not found")
    if req.total_score is not None:
        submit.total_score = req.total_score
    submit.teacher_comment = req.teacher_comment
    await db.commit()
    await db.refresh(submit)
    return api_success(_submit_dict(submit), message="Exam reviewed successfully")
