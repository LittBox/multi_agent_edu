from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.course import Course
from app.db.models.question import Question
from app.db.models.teaching_class import TeachingClass
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard/stats")
async def get_admin_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    role_rows = (
        await db.execute(
            select(User.role, func.count(User.user_id))
            .where(User.status != "deleted")
            .group_by(User.role)
        )
    ).all()
    role_counts = {role: count for role, count in role_rows}

    course_count = await db.scalar(select(func.count(Course.course_id)).where(Course.is_deleted == 0))
    class_count = await db.scalar(select(func.count(TeachingClass.class_id)).where(TeachingClass.is_deleted == 0))
    question_count = await db.scalar(select(func.count(Question.question_id)))

    roles = [
        {"role": role, "count": int(role_counts.get(role, 0))}
        for role in ("admin", "teacher", "student")
    ]

    return api_success(
        {
            "total_users": int(sum(item["count"] for item in roles)),
            "roles": roles,
            "course_count": int(course_count or 0),
            "class_count": int(class_count or 0),
            "question_count": int(question_count or 0),
        },
        message="Admin dashboard stats fetched successfully",
    )
