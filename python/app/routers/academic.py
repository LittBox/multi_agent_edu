from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success
from app.schemas.class_schedule import ClassScheduleCreate, ClassScheduleResponse
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.schemas.enrollment import (
    CourseEnrollmentCreate,
    CourseEnrollmentResponse,
    EnrolledClassInfo,
)
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.schemas.teaching_class import (
    TeachingClassCreateWithTeacher,
    TeachingClassDetail,
    TeachingClassResponse,
    TeachingClassUpdate,
)
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService
from app.services.teaching_class_service import TeachingClassService
from app.dao.classScheduleDao import ClassScheduleDAO
from app.dao.courseDao import CourseDAO
from app.dao.enrollmentDao import CourseEnrollmentDAO
from app.dao.studentDao import StudentDAO
from app.dao.teacherDao import TeacherDAO
from app.dao.teachingClassDao import TeachingClassDAO

router = APIRouter(prefix="/academic", tags=["academic"])


def _staff_role(user: User) -> str:
    return getattr(user, "role", "student")


def _require_staff(current_user: User) -> None:
    if _staff_role(current_user) not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")


async def _require_student_profile(db: AsyncSession, current_user: User):
    student = await StudentDAO.get_by_user_id(db, current_user.user_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


def _student_payload(student) -> dict:
    return StudentResponse.model_validate(student).model_dump(mode="json")


def _teacher_payload(teacher) -> dict:
    return TeacherResponse.model_validate(teacher).model_dump(mode="json")


def _course_payload(course) -> dict:
    return CourseResponse.model_validate(course).model_dump(mode="json")


def _class_payload(teaching_class) -> dict:
    return TeachingClassResponse.model_validate(teaching_class).model_dump(mode="json")


def _schedule_payload(schedule) -> dict:
    return ClassScheduleResponse.model_validate(schedule).model_dump(mode="json")


async def _class_detail_payload(db: AsyncSession, teaching_class) -> dict:
    course = await CourseDAO.get_by_id(db, teaching_class.course_id)
    teacher = await TeacherDAO.get_by_id(db, teaching_class.teacher_id)
    schedules = await ClassScheduleDAO.get_by_class(db, teaching_class.class_id)

    detail = TeachingClassDetail.model_validate(teaching_class).model_dump(mode="json")
    detail["course_name"] = course.course_name if course else None
    detail["teacher_name"] = teacher.teacher_name if teacher else None
    detail["schedules"] = [_schedule_payload(schedule) for schedule in schedules]
    return detail


async def _enrolled_class_payload(db: AsyncSession, enrollment) -> dict:
    teaching_class = await TeachingClassDAO.get_by_id(db, enrollment.class_id)
    if not teaching_class:
        return CourseEnrollmentResponse.model_validate(enrollment).model_dump(mode="json")

    course = await CourseDAO.get_by_id(db, teaching_class.course_id)
    teacher = await TeacherDAO.get_by_id(db, teaching_class.teacher_id)
    schedules = await ClassScheduleDAO.get_by_class(db, teaching_class.class_id)

    info = EnrolledClassInfo.model_validate(enrollment).model_dump(mode="json")
    info["course_name"] = course.course_name if course else ""
    info["teacher_name"] = teacher.teacher_name if teacher else ""
    info["semester"] = teaching_class.semester
    info["class_name"] = teaching_class.class_name
    info["schedules"] = [_schedule_payload(schedule) for schedule in schedules]
    return info


@router.post("/students")
async def create_student(
    req: StudentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.user_id != req.user_id:
        _require_staff(current_user)

    service = StudentService(db)
    try:
        student = await service.create_student(
            user_id=req.user_id,
            student_no=req.student_no,
            student_name=req.student_name,
            major=req.major,
            grade=req.grade,
            class_name=req.class_name,
        )
        return api_success(_student_payload(student), message="Student created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/students")
async def list_students(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = StudentService(db)
    students = await service.get_all_students()
    return api_success([_student_payload(student) for student in students], message="Students fetched successfully")


@router.get("/students/{student_id}")
async def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = StudentService(db)
    try:
        student = await service.get_student(student_id)
        if _staff_role(current_user) not in {"admin", "teacher"}:
            if student.user_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        return api_success(_student_payload(student), message="Student fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/students/by-user/{user_id}")
async def get_student_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.user_id != user_id:
        _require_staff(current_user)

    service = StudentService(db)
    try:
        student = await service.get_student_by_user(user_id)
        return api_success(_student_payload(student), message="Student fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/students/{student_id}")
async def update_student(
    student_id: int,
    req: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await StudentDAO.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if _staff_role(current_user) not in {"admin", "teacher"} and student.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    service = StudentService(db)
    try:
        updated = await service.update_student(student_id, **req.model_dump(exclude_unset=True))
        return api_success(_student_payload(updated), message="Student updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/students/{student_id}")
async def delete_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await StudentDAO.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if _staff_role(current_user) not in {"admin", "teacher"} and student.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    service = StudentService(db)
    try:
        result = await service.delete_student(student_id)
        return api_success(result, message="Student deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/teachers")
async def create_teacher(
    req: TeacherCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.user_id != req.user_id:
        _require_staff(current_user)

    service = TeacherService(db)
    try:
        teacher = await service.create_teacher(
            user_id=req.user_id,
            teacher_no=req.teacher_no,
            teacher_name=req.teacher_name,
            department=req.department,
            title=req.title,
        )
        return api_success(_teacher_payload(teacher), message="Teacher created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/teachers")
async def list_teachers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeacherService(db)
    teachers = await service.get_all_teachers()
    return api_success([_teacher_payload(teacher) for teacher in teachers], message="Teachers fetched successfully")


@router.get("/teachers/{teacher_id}")
async def get_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TeacherService(db)
    try:
        teacher = await service.get_teacher(teacher_id)
        if _staff_role(current_user) not in {"admin", "teacher"} and teacher.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        return api_success(_teacher_payload(teacher), message="Teacher fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/teachers/by-user/{user_id}")
async def get_teacher_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.user_id != user_id:
        _require_staff(current_user)

    service = TeacherService(db)
    try:
        teacher = await service.get_teacher_by_user(user_id)
        return api_success(_teacher_payload(teacher), message="Teacher fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/teachers/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    req: TeacherUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    teacher = await TeacherDAO.get_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if _staff_role(current_user) not in {"admin", "teacher"} and teacher.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    service = TeacherService(db)
    try:
        updated = await service.update_teacher(teacher_id, **req.model_dump(exclude_unset=True))
        return api_success(_teacher_payload(updated), message="Teacher updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    teacher = await TeacherDAO.get_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if _staff_role(current_user) not in {"admin", "teacher"} and teacher.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    service = TeacherService(db)
    try:
        result = await service.delete_teacher(teacher_id)
        return api_success(result, message="Teacher deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/courses")
async def create_course(
    req: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    try:
        course = await service.create_course(
            course_code=req.course_code,
            course_name=req.course_name,
            credit=req.credit,
            teacher_id=req.teacher_id,
            description=req.description,
        )
        return api_success(_course_payload(course), message="Course created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/courses")
async def list_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    courses = await service.get_all_courses()
    return api_success([_course_payload(course) for course in courses], message="Courses fetched successfully")


@router.get("/courses/{course_id}")
async def get_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    try:
        course = await service.get_course(course_id)
        return api_success(_course_payload(course), message="Course fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/teachers/{teacher_id}/courses")
async def get_teacher_courses(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    try:
        courses = await service.get_teacher_courses(teacher_id)
        return api_success([_course_payload(course) for course in courses], message="Teacher courses fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/courses/{course_id}")
async def update_course(
    course_id: int,
    req: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    try:
        updated = await service.update_course(course_id, **req.model_dump(exclude_unset=True))
        return api_success(_course_payload(updated), message="Course updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/courses/{course_id}/status")
async def update_course_status(
    course_id: int,
    status: str = Query(..., min_length=1, max_length=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    try:
        updated = await service.update_course_status(course_id, status)
        return api_success(_course_payload(updated), message="Course status updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = CourseService(db)
    try:
        result = await service.delete_course(course_id)
        return api_success(result, message="Course deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/classes")
async def create_teaching_class(
    req: TeachingClassCreateWithTeacher,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    try:
        teaching_class = await service.create_teaching_class(
            course_id=req.course_id,
            teacher_id=req.teacher_id,
            semester=req.semester,
            class_name=req.class_name,
            capacity=req.capacity,
            start_date=req.start_date,
            end_date=req.end_date,
            schedules=[schedule.model_dump(mode="python") for schedule in req.schedules],
        )
        return api_success(await _class_detail_payload(db, teaching_class), message="Teaching class created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/classes")
async def list_classes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    classes = await service.get_all_classes()
    return api_success([_class_payload(teaching_class) for teaching_class in classes], message="Teaching classes fetched successfully")


@router.get("/classes/{class_id}")
async def get_teaching_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    try:
        teaching_class = await service.get_teaching_class(class_id)
        return api_success(await _class_detail_payload(db, teaching_class), message="Teaching class fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/classes/{class_id}")
async def update_teaching_class(
    class_id: int,
    req: TeachingClassUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    try:
        updated = await service.update_teaching_class(class_id, **req.model_dump(exclude_unset=True))
        return api_success(_class_payload(updated), message="Teaching class updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/classes/{class_id}/schedules")
async def get_class_schedules(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    schedules = await service.get_class_schedules(class_id)
    return api_success([_schedule_payload(schedule) for schedule in schedules], message="Class schedules fetched successfully")


@router.get("/teachers/{teacher_id}/classes")
async def get_teacher_classes(
    teacher_id: int,
    semester: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    classes = await service.get_teacher_classes(teacher_id, semester=semester)
    return api_success([_class_payload(teaching_class) for teaching_class in classes], message="Teacher classes fetched successfully")


@router.patch("/classes/{class_id}/close")
async def close_class(
    class_id: int,
    teacher_id: int = Query(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    try:
        result = await service.close_class(class_id, teacher_id)
        return api_success(result, message="Class closed successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/classes/{class_id}/students")
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    service = TeachingClassService(db)
    enrollments = await service.get_class_students(class_id)
    return api_success(
        [CourseEnrollmentResponse.model_validate(enrollment).model_dump(mode="json") for enrollment in enrollments],
        message="Class students fetched successfully",
    )


@router.post("/enrollments")
async def enroll_student(
    req: CourseEnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await _require_student_profile(db, current_user)
    service = EnrollmentService(db)
    try:
        enrollment = await service.enroll_student(student.student_id, req.class_id)
        return api_success(
            CourseEnrollmentResponse.model_validate(enrollment).model_dump(mode="json"),
            message="Student enrolled successfully",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/enrollments/{enrollment_id}")
async def drop_enrollment(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await _require_student_profile(db, current_user)
    service = EnrollmentService(db)
    try:
        result = await service.drop_student(enrollment_id, student.student_id)
        return api_success(result, message="Enrollment dropped successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/enrollments/me")
async def get_my_enrollments(
    status: str = Query(default="enrolled", min_length=1, max_length=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await _require_student_profile(db, current_user)
    service = EnrollmentService(db)
    enrollments = await service.get_student_classes(student.student_id, status=status)
    return api_success(
        [await _enrolled_class_payload(db, enrollment) for enrollment in enrollments],
        message="Enrollments fetched successfully",
    )


@router.get("/enrollments/available")
async def get_available_classes(
    semester: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await _require_student_profile(db, current_user)
    service = EnrollmentService(db)
    classes = await service.get_available_classes(student.student_id, semester=semester)
    return api_success(
        [await _class_detail_payload(db, teaching_class) for teaching_class in classes],
        message="Available classes fetched successfully",
    )
