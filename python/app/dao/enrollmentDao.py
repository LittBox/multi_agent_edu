from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.course_enrollment import CourseEnrollment

"""
选课记录 DAO，对应 course_enrollments 表。
已适配 course_score 字段；enroll_status 只使用 enrolled / dropped。
"""

class CourseEnrollmentDAO:
    @staticmethod
    async def create_enrollment(db: AsyncSession, class_id: int, student_id: int,
                                enrolled_at: datetime | None = None,
                                course_score: float | None = None) -> CourseEnrollment:
        data = {"class_id": class_id, "student_id": student_id, "enroll_status": "enrolled"}
        if enrolled_at is not None:
            data["enrolled_at"] = enrolled_at
        if course_score is not None:
            data["course_score"] = course_score
        enrollment = CourseEnrollment(**data)
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def get_by_id(db: AsyncSession, enrollment_id: int,
                        include_deleted: bool = False) -> CourseEnrollment | None:
        conditions = [CourseEnrollment.enrollment_id == enrollment_id]
        if not include_deleted:
            conditions.append(CourseEnrollment.is_deleted == 0)
        result = await db.execute(select(CourseEnrollment).where(*conditions))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_enrollment(db: AsyncSession, student_id: int, class_id: int) -> CourseEnrollment | None:
        result = await db.execute(select(CourseEnrollment).where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.class_id == class_id,
            CourseEnrollment.enroll_status == "enrolled",
            CourseEnrollment.is_deleted == 0,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student(db: AsyncSession, student_id: int, status: str | None = "enrolled",
                             include_deleted: bool = False) -> list[CourseEnrollment]:
        conditions = [CourseEnrollment.student_id == student_id]
        if status is not None:
            conditions.append(CourseEnrollment.enroll_status == status)
        if not include_deleted:
            conditions.append(CourseEnrollment.is_deleted == 0)
        result = await db.execute(select(CourseEnrollment).where(*conditions).order_by(CourseEnrollment.enrollment_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_class(db: AsyncSession, class_id: int, status: str | None = "enrolled",
                           include_deleted: bool = False) -> list[CourseEnrollment]:
        conditions = [CourseEnrollment.class_id == class_id]
        if status is not None:
            conditions.append(CourseEnrollment.enroll_status == status)
        if not include_deleted:
            conditions.append(CourseEnrollment.is_deleted == 0)
        result = await db.execute(select(CourseEnrollment).where(*conditions).order_by(CourseEnrollment.enrollment_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def check_student_in_class(db: AsyncSession, student_id: int, class_id: int) -> bool:
        return await CourseEnrollmentDAO.get_active_enrollment(db, student_id, class_id) is not None

    @staticmethod
    async def get_all_by_student(db: AsyncSession, student_id: int) -> list[CourseEnrollment]:
        return await CourseEnrollmentDAO.get_by_student(db, student_id, status=None)

    @staticmethod
    async def update_status(db: AsyncSession, enrollment_id: int, status: str,
                            drop_reason: str | None = None,
                            dropped_at: datetime | None = None) -> CourseEnrollment | None:
        enrollment = await CourseEnrollmentDAO.get_by_id(db, enrollment_id)
        if not enrollment:
            return None
        enrollment.enroll_status = status
        if status == "dropped":
            enrollment.dropped_at = dropped_at or datetime.now(UTC)
            if drop_reason is not None:
                enrollment.drop_reason = drop_reason
        elif status == "enrolled":
            enrollment.dropped_at = None
            enrollment.drop_reason = None
        enrollment.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def drop_enrollment(db: AsyncSession, enrollment_id: int,
                              drop_reason: str | None = None) -> CourseEnrollment | None:
        return await CourseEnrollmentDAO.update_status(db, enrollment_id, "dropped", drop_reason=drop_reason)

    @staticmethod
    async def update_score(db: AsyncSession, enrollment_id: int,
                           course_score: float | None) -> CourseEnrollment | None:
        enrollment = await CourseEnrollmentDAO.get_by_id(db, enrollment_id)
        if not enrollment:
            return None
        enrollment.course_score = course_score
        enrollment.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def soft_delete(db: AsyncSession, enrollment_id: int) -> bool:
        enrollment = await CourseEnrollmentDAO.get_by_id(db, enrollment_id)
        if not enrollment:
            return False
        enrollment.is_deleted = 1
        enrollment.updated_at = datetime.now(UTC)
        await db.commit()
        return True
