from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.review_schedule import ReviewSchedule


class ReviewScheduleDAO:

    @staticmethod
    async def create_schedule(
        db: AsyncSession,
        user_id: int,
        knowledge_id: int,
        ef: float | None = None,
        interval_days: int | None = None,
        repetition: int | None = None,
        last_review_at: datetime | None = None,
        next_review_at: datetime | None = None
    ) -> ReviewSchedule:

        data: dict[str, object] = {
            "user_id": user_id,
            "knowledge_id": knowledge_id,
            "last_review_at": last_review_at,
            "next_review_at": next_review_at
        }

        if ef is not None:
            data["ef"] = ef

        if interval_days is not None:
            data["interval_days"] = interval_days

        if repetition is not None:
            data["repetition"] = repetition

        schedule = ReviewSchedule(**data)

        db.add(schedule)

        await db.commit()

        await db.refresh(schedule)

        return schedule

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        schedule_id: int
    ) -> ReviewSchedule | None:

        result = await db.execute(
            select(ReviewSchedule).where(
                ReviewSchedule.schedule_id == schedule_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user_knowledge(
        db: AsyncSession,
        user_id: int,
        knowledge_id: int
    ) -> ReviewSchedule | None:

        result = await db.execute(
            select(ReviewSchedule).where(
                ReviewSchedule.user_id == user_id,
                ReviewSchedule.knowledge_id == knowledge_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession
    ):

        result = await db.execute(
            select(ReviewSchedule)
        )

        return result.scalars().all()

    @staticmethod
    async def delete_schedule(
        db: AsyncSession,
        schedule_id: int
    ) -> bool:

        schedule = await ReviewScheduleDAO.get_by_id(
            db,
            schedule_id
        )

        if not schedule:
            return False

        await db.delete(schedule)

        await db.commit()

        return True

    @staticmethod
    async def update_schedule(
        db: AsyncSession,
        schedule_id: int,
        ef: float | None = None,
        interval_days: int | None = None,
        repetition: int | None = None,
        last_review_at: datetime | None = None,
        next_review_at: datetime | None = None
    ) -> ReviewSchedule | None:

        schedule = await ReviewScheduleDAO.get_by_id(
            db,
            schedule_id
        )

        if not schedule:
            return None

        if ef is not None:
            schedule.ef = ef

        if interval_days is not None:
            schedule.interval_days = interval_days

        if repetition is not None:
            schedule.repetition = repetition

        if last_review_at is not None:
            schedule.last_review_at = last_review_at

        if next_review_at is not None:
            schedule.next_review_at = next_review_at

        await db.commit()

        await db.refresh(schedule)

        return schedule
    
    @staticmethod
    async def upsert_schedule(
        db: AsyncSession,
        user_id: int,
        knowledge_id: int,
        ef: float | None = None,
        interval_days: int | None = None,
        repetition: int | None = None,
        last_review_at: datetime | None = None,
        next_review_at: datetime | None = None
    ) -> ReviewSchedule:

        schedule = await ReviewScheduleDAO.get_by_user_knowledge(
            db,
            user_id,
            knowledge_id
        )

        if schedule:
            return await ReviewScheduleDAO.update_schedule(
                db,
                schedule.schedule_id,
                ef,
                interval_days,
                repetition,
                last_review_at,
                next_review_at
            )

        return await ReviewScheduleDAO.create_schedule(
            db,
            user_id,
            knowledge_id,
            ef,
            interval_days,
            repetition,
            last_review_at,
            next_review_at
        )