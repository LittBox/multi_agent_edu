import asyncio

from app.db.base import Base
from app.db.database import engine
from app.db.models import (
    User,
    KnowledgePoint,
    Question,
    AnswerRecord,
    LearnerState,
    ReviewSchedule,
    Student,
    Teacher,
    Course,
    TeachingClass,
    ClassSchedule,
    CourseEnrollment,
)



async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(main())
