from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.course_enrollment import CourseEnrollment

"""
选课记录数据访问对象（DAO，Data Access Object），提供对选课记录表的增删改查操作，包括创建选课记录、根据ID查询选课记录、根据学生ID查询选课记录列表、根据教学班ID查询选课记录列表、检查学生是否已选某教学班、更新选课状态、删除选课记录等功能。
选课记录DAO的主要职责包括：
1. 创建选课记录：根据教学班ID、学生ID等信息创建新的选课记录，并设置选课状态为“enrolled”。
2. 根据ID查询选课记录：根据选课记录ID查询选课记录的详细信息，包括教学班ID、学生ID、选课状态、选课时间等信息。
3. 根据学生ID查询选课记录列表：根据学生ID查询该学生的所有选课记录，并返回一个列表，包含每条记录的详细信息。
4. 根据教学班ID查询选课记录列表：根据教学班ID查询该教学班的所有选课记录，并返回一个列表，包含每条记录的详细信息。
5. 检查学生是否已选某教学班：根据学生ID和教学班ID检查该学生是否已选该教学班，并返回布尔值。
6. 更新选课状态：根据选课记录ID更新选课状态，例如将选课状态从“enrolled”变更为“dropped”，并记录退课时间和退课原因等信息。
7. 删除选课记录：根据选课记录ID删除选课记录，实际操作为软删除，即将记录的状态标记为“deleted”，以保留历史数据。
"""
class CourseEnrollmentDAO:

    @staticmethod
    async def create_enrollment(
        db: AsyncSession,
        class_id: int,
        student_id: int,
    ) -> CourseEnrollment:
        enrollment = CourseEnrollment(
            class_id=class_id,
            student_id=student_id,
            enroll_status="enrolled",
        )
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def get_by_id(db: AsyncSession, enrollment_id: int) -> CourseEnrollment | None:
        result = await db.execute(
            select(CourseEnrollment).where(
                CourseEnrollment.enrollment_id == enrollment_id,
                CourseEnrollment.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_enrollment(
        db: AsyncSession,
        student_id: int,
        class_id: int
    ) -> CourseEnrollment | None:
        result = await db.execute(
            select(CourseEnrollment).where(
                and_(
                    CourseEnrollment.student_id == student_id,
                    CourseEnrollment.class_id == class_id,
                    CourseEnrollment.enroll_status == "enrolled",
                    CourseEnrollment.is_deleted == 0
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_student(db: AsyncSession, student_id: int, status: str = "enrolled"):
        result = await db.execute(
            select(CourseEnrollment).where(
                and_(
                    CourseEnrollment.student_id == student_id,
                    CourseEnrollment.enroll_status == status,
                    CourseEnrollment.is_deleted == 0
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_class(db: AsyncSession, class_id: int, status: str = "enrolled"):
        result = await db.execute(
            select(CourseEnrollment).where(
                and_(
                    CourseEnrollment.class_id == class_id,
                    CourseEnrollment.enroll_status == status,
                    CourseEnrollment.is_deleted == 0
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def check_student_in_class(
        db: AsyncSession,
        student_id: int,
        class_id: int
    ) -> bool:
        enrollment = await CourseEnrollmentDAO.get_active_enrollment(db, student_id, class_id)
        return enrollment is not None

    @staticmethod
    async def update_status(
        db: AsyncSession,
        enrollment_id: int,
        status: str,
        drop_reason: str | None = None
    ) -> CourseEnrollment | None:
        enrollment = await CourseEnrollmentDAO.get_by_id(db, enrollment_id)
        if not enrollment:
            return None

        enrollment.enroll_status = status
        if status == "dropped":
            from datetime import datetime, UTC
            enrollment.dropped_at = datetime.now(UTC)
            if drop_reason:
                enrollment.drop_reason = drop_reason

        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def get_all_by_student(db: AsyncSession, student_id: int):
        result = await db.execute(
            select(CourseEnrollment).where(
                and_(
                    CourseEnrollment.student_id == student_id,
                    CourseEnrollment.is_deleted == 0
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def soft_delete(db: AsyncSession, enrollment_id: int) -> bool:
        enrollment = await CourseEnrollmentDAO.get_by_id(db, enrollment_id)
        if not enrollment:
            return False

        enrollment.is_deleted = 1
        await db.commit()
        return True
