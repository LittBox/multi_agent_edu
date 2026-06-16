"""作业路由。

对应前端 TaskView：
- GET /tasks/bank：教师端作业题库
- POST /tasks/bank：教师创建作业
- POST /tasks/releases：教师发布作业
- GET /tasks/releases：学生端上方“已发布作业”
- POST /tasks/releases/{task_publish_id}/submit：学生提交作业
- GET /tasks/submissions/me：学生端下方“我的作业进度”
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskBankCreateIn(BaseModel):
    """创建作业题库条目。前端传 course_id/task_type/task_content。"""
    course_id: int
    task_type: str = "homework"
    task_content: str = Field(min_length=1)


class TaskBankUpdateIn(BaseModel):
    """更新作业题库条目。"""
    course_id: int | None = None
    teacher_id: int | None = None
    task_type: str | None = None
    task_content: str | None = Field(default=None, min_length=1)


class TaskReleaseIn(BaseModel):
    """发布作业。"""
    task_id: int
    deadline: datetime | None = None


class TaskReleaseUpdateIn(BaseModel):
    """更新作业发布信息。"""
    deadline: datetime | None = None
    is_deleted: int | None = None


class TaskSubmitIn(BaseModel):
    """学生提交作业。"""
    answer_content: str = Field(min_length=1)


class TaskGradeIn(BaseModel):
    """教师批改作业。"""
    score: float = Field(ge=0)
    comment: str | None = None


def _require_staff(user: User) -> None:
    if user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")


def _require_student(user: User) -> None:
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this resource")


@router.get("/bank")
async def list_task_bank(course_id: int | None = Query(default=None), teacher_id: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师/管理员查看作业题库。"""
    _require_staff(current_user)
    data = await TaskService(db).list_bank(course_id=course_id, teacher_id=teacher_id)
    return api_success(data, message="Task bank fetched successfully")


@router.post("/bank")
async def create_task(req: TaskBankCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师创建作业题库条目。"""
    _require_staff(current_user)
    try:
        data = await TaskService(db).create_bank_by_user(current_user.user_id, req.course_id, req.task_type, req.task_content)
        return api_success(data, message="Task created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/bank/{task_id}")
async def update_task(task_id: int, req: TaskBankUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新作业题库条目。"""
    _require_staff(current_user)
    try:
        data = await TaskService(db).update_bank(task_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Task updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/bank/{task_id}")
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """软删除作业题库条目。"""
    _require_staff(current_user)
    try:
        ok = await TaskService(db).delete_bank(task_id)
        return api_success(ok, message="Task deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# 兼容旧前端：/tasks/questions 等价于 /tasks/bank
@router.get("/questions")
async def list_task_questions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await list_task_bank(current_user=current_user, db=db)


@router.post("/questions")
async def create_task_question(req: TaskBankCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_task(req, current_user, db)


@router.post("/releases")
async def release_task(req: TaskReleaseIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师发布作业。"""
    _require_staff(current_user)
    try:
        data = await TaskService(db).release(req.task_id, deadline=req.deadline)
        return api_success(data, message="Task released successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/releases")
async def list_releases(task_id: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """查询已发布作业，学生端和教师端共用。"""
    data = await TaskService(db).list_releases(task_id=task_id)
    return api_success(data, message="Task releases fetched successfully")


@router.patch("/releases/{task_publish_id}")
async def update_release(task_publish_id: int, req: TaskReleaseUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新作业发布信息。"""
    _require_staff(current_user)
    try:
        data = await TaskService(db).update_release(task_publish_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Task release updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/releases/{task_publish_id}")
async def delete_release(task_publish_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """软删除作业发布记录。"""
    _require_staff(current_user)
    try:
        ok = await TaskService(db).delete_release(task_publish_id)
        return api_success(ok, message="Task release deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/releases/{task_publish_id}/submit")
async def submit_task(task_publish_id: int, req: TaskSubmitIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生提交作业；重复提交时由 DAO/service 执行更新。"""
    _require_student(current_user)
    try:
        data = await TaskService(db).submit(task_publish_id, current_user.user_id, req.answer_content)
        return api_success(data, message="Task submitted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/submissions/me")
async def my_task_submissions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生查看自己的作业提交记录。"""
    _require_student(current_user)
    try:
        data = await TaskService(db).my_submissions(current_user.user_id)
        return api_success(data, message="Task submissions fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/submissions/{submit_id}/grade")
async def grade_task(submit_id: int, req: TaskGradeIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师批改作业。"""
    _require_staff(current_user)
    try:
        data = await TaskService(db).grade_submission(submit_id, req.score, req.comment)
        return api_success(data, message="Task graded successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
