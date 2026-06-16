from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.review_schedule import ReviewSchedule

"""
复习计划 DAO，对应 review_schedules 表。
user_id + knowledge_id 唯一；记录 ef、interval_days、repetition、last_review_at、next_review_at。
"""

class ReviewScheduleDAO:
    @staticmethod
    async def create_schedule(db: AsyncSession, user_id: int, knowledge_id: int,
                              ef: float | None = None, interval_days: int | None = None,
                              repetition: int | None = None,
                              last_review_at: datetime | None = None,
                              next_review_at: datetime | None = None) -> ReviewSchedule:
        data = {"user_id": user_id, "knowledge_id": knowledge_id}
        for key, value in {
            "ef": ef, "interval_days": interval_days, "repetition": repetition,
            "last_review_at": last_review_at, "next_review_at": next_review_at,
        }.items():
            if value is not None:
                data[key] = value
        schedule = ReviewSchedule(**data)
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    @staticmethod
    async def get_by_id(db: AsyncSession, schedule_id: int) -> ReviewSchedule | None:
        result = await db.execute(select(ReviewSchedule).where(ReviewSchedule.schedule_id == schedule_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_knowledge(db: AsyncSession, user_id: int, knowledge_id: int) -> ReviewSchedule | None:
        result = await db.execute(select(ReviewSchedule).where(
            ReviewSchedule.user_id == user_id,
            ReviewSchedule.knowledge_id == knowledge_id,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> list[ReviewSchedule]:
        result = await db.execute(
            select(ReviewSchedule)
            .where(ReviewSchedule.user_id == user_id)
            .order_by(ReviewSchedule.next_review_at.asc().nullslast())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_due_schedules(db: AsyncSession, user_id: int | None = None,
                                now: datetime | None = None) -> list[ReviewSchedule]:
        due_time = now or datetime.now(UTC)
        conditions = [ReviewSchedule.next_review_at.is_not(None), ReviewSchedule.next_review_at <= due_time]
        if user_id is not None:
            conditions.append(ReviewSchedule.user_id == user_id)
        result = await db.execute(select(ReviewSchedule).where(*conditions).order_by(ReviewSchedule.next_review_at.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_all(db: AsyncSession) -> list[ReviewSchedule]:
        result = await db.execute(select(ReviewSchedule).order_by(ReviewSchedule.schedule_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_schedule(db: AsyncSession, schedule_id: int, **kwargs) -> ReviewSchedule | None:
        schedule = await ReviewScheduleDAO.get_by_id(db, schedule_id)
        if not schedule:
            return None
        for key in ("ef", "interval_days", "repetition", "last_review_at", "next_review_at"):
            if key in kwargs and kwargs[key] is not None:
                setattr(schedule, key, kwargs[key])
        schedule.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    @staticmethod
    async def upsert_schedule(db: AsyncSession, user_id: int, knowledge_id: int, **kwargs) -> ReviewSchedule:
        schedule = await ReviewScheduleDAO.get_by_user_knowledge(db, user_id, knowledge_id)
        if schedule:
            updated = await ReviewScheduleDAO.update_schedule(db, schedule.schedule_id, **kwargs)
            assert updated is not None
            return updated
        return await ReviewScheduleDAO.create_schedule(db, user_id=user_id, knowledge_id=knowledge_id, **kwargs)

    @staticmethod
    async def delete_schedule(db: AsyncSession, schedule_id: int) -> bool:
        schedule = await ReviewScheduleDAO.get_by_id(db, schedule_id)
        if not schedule:
            return False
        await db.delete(schedule)
        await db.commit()
        return True
