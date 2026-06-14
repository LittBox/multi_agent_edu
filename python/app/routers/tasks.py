from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.student import Student
from app.db.models.task import TaskBank, TaskRelease, TaskSubmission
from app.db.models.teacher import Teacher
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskQuestionIn(BaseModel):
    course_id: int
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    question_type: str = "homework"
    difficulty: int = Field(default=1, ge=1, le=5)


class TaskQuestionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    question_type: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=5)


class TaskReleaseIn(BaseModel):
    task_id: int
    deadline: datetime | None = None


class TaskSubmitIn(BaseModel):
    answer_content: str = Field(min_length=1)


class TaskGradeIn(BaseModel):
    score: float
    comment: str | None = None


async def _teacher_id(db: AsyncSession, user: User) -> int:
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access task question bank")
    teacher = (await db.execute(select(Teacher).where(Teacher.user_id == user.user_id, Teacher.is_deleted == 0))).scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=400, detail="当前用户没有绑定教师档案，不能创建题目。请联系管理员。")
    return teacher.teacher_id


async def _student_id(db: AsyncSession, user: User) -> int:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit tasks")
    student = (await db.execute(select(Student).where(Student.user_id == user.user_id, Student.is_deleted == 0))).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=400, detail="当前用户没有绑定学生档案，不能提交作业。请联系管理员。")
    return student.student_id


def _task_dict(task: TaskBank) -> dict:
    title, _, content = (task.task_content or "").partition("\n")
    return {
        "question_id": task.task_id,
        "task_id": task.task_id,
        "course_id": task.course_id,
        "teacher_id": task.teacher_id,
        "title": title or "未命名题目",
        "content": content or task.task_content,
        "question_type": task.task_type,
        "difficulty": 1,
        "task_type": task.task_type,
        "task_content": task.task_content,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


def _release_dict(release: TaskRelease) -> dict:
    task = release.task
    return {
        "task_publish_id": release.task_publish_id,
        "task_id": release.task_id,
        "publish_time": release.publish_time,
        "deadline": release.deadline,
        "task_content": task.task_content if task else None,
        "task_type": task.task_type if task else None,
        "course_id": task.course_id if task else None,
    }


def _submission_dict(submission: TaskSubmission) -> dict:
    return {
        "submit_id": submission.submit_id,
        "task_publish_id": submission.task_publish_id,
        "student_id": submission.student_id,
        "submit_time": submission.submit_time,
        "answer_content": submission.answer_content,
        "score": submission.score,
        "comment": submission.comment,
    }


@router.get("/questions")
async def list_task_questions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    teacher_id = await _teacher_id(db, current_user)
    tasks = (await db.execute(select(TaskBank).where(TaskBank.teacher_id == teacher_id, TaskBank.is_deleted == 0).order_by(TaskBank.created_at.desc()))).scalars().all()
    return api_success([_task_dict(task) for task in tasks], message="Task questions fetched successfully")


@router.post("/questions")
async def create_task_question(req: TaskQuestionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    teacher_id = await _teacher_id(db, current_user)
    task = TaskBank(
        course_id=req.course_id,
        teacher_id=teacher_id,
        task_type=req.question_type,
        task_content=f"{req.title}\n{req.content}",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return api_success(_task_dict(task), message="Task question created successfully")


@router.put("/questions/{question_id}")
async def update_task_question(question_id: int, req: TaskQuestionUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    teacher_id = await _teacher_id(db, current_user)
    task = await db.get(TaskBank, question_id)
    if not task or task.is_deleted or task.teacher_id != teacher_id:
        raise HTTPException(status_code=404, detail="Task question not found")
    current = _task_dict(task)
    title = req.title if req.title is not None else current["title"]
    content = req.content if req.content is not None else current["content"]
    task.task_content = f"{title}\n{content}"
    if req.question_type is not None:
        task.task_type = req.question_type
    await db.commit()
    await db.refresh(task)
    return api_success(_task_dict(task), message="Task question updated successfully")


@router.delete("/questions/{question_id}")
async def delete_task_question(question_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    teacher_id = await _teacher_id(db, current_user)
    task = await db.get(TaskBank, question_id)
    if not task or task.is_deleted or task.teacher_id != teacher_id:
        raise HTTPException(status_code=404, detail="Task question not found")
    task.is_deleted = 1
    await db.commit()
    return api_success({"question_id": question_id}, message="Task question deleted successfully")


@router.get("/bank")
async def list_task_bank(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_task_questions(current_user, db)


@router.post("/bank")
async def create_task(req: TaskQuestionIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_task_question(req, current_user, db)


@router.delete("/bank/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await delete_task_question(task_id, current_user, db)


@router.post("/releases")
async def release_task(req: TaskReleaseIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    teacher_id = await _teacher_id(db, current_user)
    task = await db.get(TaskBank, req.task_id)
    if not task or task.is_deleted or task.teacher_id != teacher_id:
        raise HTTPException(status_code=404, detail="Task question not found")
    release = TaskRelease(task_id=req.task_id, deadline=req.deadline, publish_time=datetime.now(UTC))
    db.add(release)
    await db.commit()
    await db.refresh(release, ["task"])
    return api_success(_release_dict(release), message="Task released successfully")


@router.get("/releases")
async def list_releases(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role not in {"teacher", "student"}:
        raise HTTPException(status_code=403, detail="Permission denied")
    releases = (await db.execute(select(TaskRelease).where(TaskRelease.is_deleted == 0).order_by(TaskRelease.publish_time.desc()))).scalars().all()
    return api_success([_release_dict(release) for release in releases], message="Task releases fetched successfully")


@router.post("/releases/{task_publish_id}/submit")
async def submit_task(task_publish_id: int, req: TaskSubmitIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    student_id = await _student_id(db, current_user)
    release = await db.get(TaskRelease, task_publish_id)
    if not release or release.is_deleted:
        raise HTTPException(status_code=404, detail="Task release not found")
    existing = (await db.execute(select(TaskSubmission).where(TaskSubmission.task_publish_id == task_publish_id, TaskSubmission.student_id == student_id))).scalar_one_or_none()
    if existing:
        existing.answer_content = req.answer_content
        existing.submit_time = datetime.now(UTC)
        existing.score = None
        existing.comment = None
        submission = existing
    else:
        submission = TaskSubmission(task_publish_id=task_publish_id, student_id=student_id, answer_content=req.answer_content)
        db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return api_success(_submission_dict(submission), message="Task submitted successfully")


@router.get("/submissions/me")
async def my_task_submissions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    student_id = await _student_id(db, current_user)
    submissions = (await db.execute(select(TaskSubmission).where(TaskSubmission.student_id == student_id).order_by(TaskSubmission.submit_time.desc()))).scalars().all()
    return api_success([_submission_dict(item) for item in submissions], message="Task submissions fetched successfully")


@router.get("/releases/{task_publish_id}/submissions")
async def release_submissions(task_publish_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _teacher_id(db, current_user)
    submissions = (await db.execute(select(TaskSubmission).where(TaskSubmission.task_publish_id == task_publish_id).order_by(TaskSubmission.submit_time.desc()))).scalars().all()
    return api_success([_submission_dict(item) for item in submissions], message="Task submissions fetched successfully")


@router.put("/submissions/{submit_id}/grade")
async def grade_task(submit_id: int, req: TaskGradeIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await _teacher_id(db, current_user)
    submission = await db.get(TaskSubmission, submit_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission.score = req.score
    submission.comment = req.comment
    await db.commit()
    await db.refresh(submission)
    return api_success(_submission_dict(submission), message="Task graded successfully")
