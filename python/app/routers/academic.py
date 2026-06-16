"""教务相关路由。

本文件负责把前端教务模块的 HTTP 请求转发到 service 层：
- 学生/教师档案管理
- 课程管理
- 教学班管理
- 学生选课、退课、查看可选课程和已选课程

约定：
1. router 层只做权限校验、参数接收、异常转换和统一响应包装。
2. 具体业务规则放在 service 层，例如容量校验、时间冲突、重复选课等。
3. 返回给前端的数据直接使用 service 层整理好的 dict，避免重复序列化逻辑。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.api_response import api_success
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.services.student_service import StudentService
from app.services.teacher_service import TeacherService
from app.services.teaching_class_service import TeachingClassService

router = APIRouter(prefix="/academic", tags=["academic"])


# =========================
# 请求体模型
# =========================
class StudentCreateIn(BaseModel):
    """创建学生档案请求体。user_id 必须指向已存在的 users.user_id。"""
    user_id: int
    student_no: str = Field(min_length=1, max_length=50)
    student_name: str = Field(min_length=1, max_length=100)
    major: str | None = None
    grade: int | None = None
    class_name: str | None = None


class StudentUpdateIn(BaseModel):
    """更新学生档案请求体，所有字段可选。"""
    student_no: str | None = None
    student_name: str | None = None
    major: str | None = None
    grade: int | None = None
    class_name: str | None = None


class TeacherCreateIn(BaseModel):
    """创建教师档案请求体。user_id 必须指向已存在的 users.user_id。"""
    user_id: int
    teacher_no: str = Field(min_length=1, max_length=50)
    teacher_name: str = Field(min_length=1, max_length=100)
    department: str | None = None
    title: str | None = None


class TeacherUpdateIn(BaseModel):
    """更新教师档案请求体，所有字段可选。"""
    teacher_no: str | None = None
    teacher_name: str | None = None
    department: str | None = None
    title: str | None = None


class CourseCreateIn(BaseModel):
    """创建课程请求体。教师端通常不传 teacher_id，由当前登录教师决定。"""
    course_code: str = Field(min_length=1, max_length=50)
    course_name: str = Field(min_length=1, max_length=200)
    credit: float = Field(gt=0)
    description: str | None = None
    teacher_id: int | None = None
    status: str = "active"


class CourseUpdateIn(BaseModel):
    """更新课程请求体。"""
    course_code: str | None = None
    course_name: str | None = None
    credit: float | None = Field(default=None, gt=0)
    description: str | None = None
    created_by_teacher_id: int | None = None
    status: str | None = None


class ScheduleIn(BaseModel):
    """教学班上课安排。

    前端可传 weekday/start_time/end_time，也兼容 day/time 格式。
    """
    weekday: int | None = Field(default=None, ge=1, le=7)
    day: int | None = Field(default=None, ge=1, le=7)
    start_time: str | None = None
    end_time: str | None = None
    time: str | None = None
    week_start: int | None = None
    week_end: int | None = None
    classroom: str | None = None


class TeachingClassCreateIn(BaseModel):
    """创建教学班请求体。teacher_id 可选；教师端默认使用当前教师档案。"""
    course_id: int
    teacher_id: int | None = None
    semester: str = Field(min_length=1, max_length=50)
    class_name: str = Field(min_length=1, max_length=100)
    capacity: int = Field(gt=0)
    location: str | None = None
    start_week: int = Field(gt=0)
    end_week: int = Field(gt=0)
    schedules: list[ScheduleIn] = Field(default_factory=list)


class TeachingClassUpdateIn(BaseModel):
    """更新教学班请求体。"""
    course_id: int | None = None
    teacher_id: int | None = None
    semester: str | None = None
    class_name: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    location: str | None = None
    current_count: int | None = Field(default=None, ge=0)
    start_week: int | None = Field(default=None, gt=0)
    end_week: int | None = Field(default=None, gt=0)
    status: str | None = None
    schedules: list[dict] | None = None


class EnrollmentCreateIn(BaseModel):
    """学生选课请求体。前端只需要传 class_id。"""
    class_id: int


class DropEnrollmentIn(BaseModel):
    """退课请求体。drop_reason 不传时 service 层使用默认原因。"""
    drop_reason: str | None = None


class ScoreUpdateIn(BaseModel):
    """教师录入或更新课程成绩。"""
    course_score: float | None = Field(default=None, ge=0, le=100)


# =========================
# 权限辅助函数
# =========================
def _role(user: User) -> str:
    """读取当前用户角色，缺省按学生处理。"""
    return getattr(user, "role", "student")


def _require_staff(user: User) -> None:
    """仅管理员或教师可访问。"""
    if _role(user) not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Permission denied")


def _require_admin(user: User) -> None:
    """仅管理员可访问。"""
    if _role(user) != "admin":
        raise HTTPException(status_code=403, detail="Admin only")


async def _current_teacher_id(db: AsyncSession, user: User) -> int:
    """获取当前登录教师的 teacher_id。"""
    if _role(user) != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access this resource")
    teacher = await TeacherService(db).get_teacher_by_user(user.user_id)
    return teacher["teacher_id"]


def _schedule_payload(items: list[ScheduleIn]) -> list[dict]:
    """把前端 schedule 请求体转换为 service 层使用的 JSONB 字典列表。"""
    schedules: list[dict] = []
    for item in items:
        raw = item.model_dump(exclude_none=True)
        weekday = raw.get("weekday") or raw.get("day")
        if not weekday:
            raise HTTPException(status_code=400, detail="Schedule weekday is required")
        if raw.get("time") and (not raw.get("start_time") or not raw.get("end_time")):
            parts = str(raw["time"]).split("-")
            if len(parts) == 2:
                raw["start_time"] = parts[0].strip()
                raw["end_time"] = parts[1].strip()
        if not raw.get("start_time") or not raw.get("end_time"):
            raise HTTPException(status_code=400, detail="Schedule start_time and end_time are required")
        raw["weekday"] = weekday
        raw["day"] = weekday
        raw["time"] = f"{raw['start_time']}-{raw['end_time']}"
        schedules.append(raw)
    return schedules


# =========================
# 学生档案
# =========================
@router.post("/students")
async def create_student(req: StudentCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.user_id != req.user_id:
        _require_staff(current_user)
    try:
        data = await StudentService(db).create_student(**req.model_dump())
        return api_success(data, message="Student created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/students")
async def list_students(major: str | None = Query(default=None), grade: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    data = await StudentService(db).list_students(major=major, grade=grade)
    return api_success(data, message="Students fetched successfully")


@router.get("/students/{student_id}")
async def get_student(student_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        data = await StudentService(db).get_student(student_id)
        if _role(current_user) == "student" and data["user_id"] != current_user.user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        return api_success(data, message="Student fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/students/by-user/{user_id}")
async def get_student_by_user(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.user_id != user_id:
        _require_staff(current_user)
    try:
        data = await StudentService(db).get_student_by_user(user_id)
        return api_success(data, message="Student fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/students/{student_id}")
async def update_student(student_id: int, req: StudentUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current = await StudentService(db).get_student(student_id)
    if _role(current_user) == "student" and current["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    try:
        data = await StudentService(db).update_student(student_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Student updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/students/{student_id}")
async def delete_student(student_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        ok = await StudentService(db).delete_student(student_id)
        return api_success(ok, message="Student deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =========================
# 教师档案
# =========================
@router.post("/teachers")
async def create_teacher(req: TeacherCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.user_id != req.user_id:
        _require_admin(current_user)
    try:
        data = await TeacherService(db).create_teacher(**req.model_dump())
        return api_success(data, message="Teacher created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/teachers")
async def list_teachers(department: str | None = Query(default=None), title: str | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    data = await TeacherService(db).list_teachers(department=department, title=title)
    return api_success(data, message="Teachers fetched successfully")


@router.get("/teachers/{teacher_id}")
async def get_teacher(teacher_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        data = await TeacherService(db).get_teacher(teacher_id)
        if _role(current_user) == "teacher" and data["user_id"] != current_user.user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        return api_success(data, message="Teacher fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/teachers/by-user/{user_id}")
async def get_teacher_by_user(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.user_id != user_id:
        _require_staff(current_user)
    try:
        data = await TeacherService(db).get_teacher_by_user(user_id)
        return api_success(data, message="Teacher fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/teachers/{teacher_id}")
async def update_teacher(teacher_id: int, req: TeacherUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current = await TeacherService(db).get_teacher(teacher_id)
    if _role(current_user) == "teacher" and current["user_id"] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    try:
        data = await TeacherService(db).update_teacher(teacher_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Teacher updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/teachers/{teacher_id}")
async def delete_teacher(teacher_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_admin(current_user)
    try:
        ok = await TeacherService(db).delete_teacher(teacher_id)
        return api_success(ok, message="Teacher deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =========================
# 课程管理
# =========================
@router.post("/courses")
async def create_course(req: CourseCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if _role(current_user) == "teacher":
        teacher_id = await _current_teacher_id(db, current_user)
    else:
        _require_admin(current_user)
        if req.teacher_id is None:
            raise HTTPException(status_code=400, detail="teacher_id is required for admin")
        teacher_id = req.teacher_id
    try:
        data = await CourseService(db).create_course(
            course_code=req.course_code,
            course_name=req.course_name,
            credit=req.credit,
            teacher_id=teacher_id,
            description=req.description,
            status=req.status,
        )
        return api_success(data, message="Course created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/courses")
async def list_courses(status: str | None = Query(default=None), q: str | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    data = await CourseService(db).get_all_courses(status=status, q=q)
    return api_success(data, message="Courses fetched successfully")


@router.get("/courses/{course_id}")
async def get_course(course_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await CourseService(db).get_course(course_id)
        return api_success(data, message="Course fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/courses/{course_id}")
async def update_course(course_id: int, req: CourseUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await CourseService(db).update_course(course_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Course updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/courses/{course_id}/status")
async def update_course_status(course_id: int, status: str = Query(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await CourseService(db).update_course_status(course_id, status)
        return api_success(data, message="Course status updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        ok = await CourseService(db).delete_course(course_id)
        return api_success(ok, message="Course deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/teachers/{teacher_id}/courses")
async def get_teacher_courses(teacher_id: int, status: str | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await CourseService(db).get_teacher_courses(teacher_id, status=status)
        return api_success(data, message="Teacher courses fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/courses/{course_id}/classes")
async def get_course_classes(course_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await CourseService(db).get_course_classes(course_id)
        return api_success(data, message="Course classes fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =========================
# 教学班管理
# =========================
@router.post("/classes")
async def create_teaching_class(req: TeachingClassCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    teacher_id = await _current_teacher_id(db, current_user) if _role(current_user) == "teacher" else req.teacher_id
    if teacher_id is None:
        _require_admin(current_user)
        raise HTTPException(status_code=400, detail="teacher_id is required")
    try:
        data = await TeachingClassService(db).create_teaching_class(
            course_id=req.course_id,
            teacher_id=teacher_id,
            semester=req.semester,
            class_name=req.class_name,
            capacity=req.capacity,
            start_week=req.start_week,
            end_week=req.end_week,
            schedules=_schedule_payload(req.schedules),
            location=req.location,
        )
        return api_success(data, message="Teaching class created successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/classes")
async def list_classes(status: str | None = Query(default=None), semester: str | None = Query(default=None), teacher_id: int | None = Query(default=None), course_id: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    data = await TeachingClassService(db).list_classes(status=status, semester=semester, teacher_id=teacher_id, course_id=course_id)
    return api_success(data, message="Teaching classes fetched successfully")


@router.get("/classes/available")
async def list_available_classes_for_staff(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    data = await TeachingClassService(db).list_available_classes()
    return api_success(data, message="Available classes fetched successfully")


@router.get("/classes/{class_id}")
async def get_teaching_class(class_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await TeachingClassService(db).get_teaching_class(class_id)
        return api_success(data, message="Teaching class fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/classes/{class_id}")
async def update_teaching_class(class_id: int, req: TeachingClassUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await TeachingClassService(db).update_teaching_class(class_id, **req.model_dump(exclude_unset=True))
        return api_success(data, message="Teaching class updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/classes/{class_id}/status")
async def update_class_status(class_id: int, status: str = Query(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await TeachingClassService(db).update_status(class_id, status)
        return api_success(data, message="Teaching class status updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/classes/{class_id}")
async def delete_class(class_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        ok = await TeachingClassService(db).delete_class(class_id)
        return api_success(ok, message="Teaching class deleted successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/classes/{class_id}/students")
async def get_class_students(class_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_staff(current_user)
    try:
        data = await TeachingClassService(db).get_class_students(class_id)
        return api_success(data, message="Class students fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# =========================
# 学生选课接口，对应前端 StudentCourseView
# =========================
@router.get("/enrollments/available")
async def get_available_classes(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生端上方区域：所有公开可选教学班。"""
    try:
        data = await EnrollmentService(db).list_available_classes()
        return api_success(data, message="Available classes fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/enrollments/me")
async def get_my_enrollments(status: str | None = Query(default="enrolled"), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生端下方区域：当前学生已选课程。"""
    try:
        data = await EnrollmentService(db).list_my_enrollments(current_user.user_id, status=status)
        return api_success(data, message="Enrollments fetched successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/enrollments")
async def enroll_student(req: EnrollmentCreateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生加入课程。"""
    try:
        data = await EnrollmentService(db).enroll_by_user(current_user.user_id, req.class_id)
        return api_success(data, message="Student enrolled successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/enrollments/{enrollment_id}")
async def drop_enrollment(enrollment_id: int, req: DropEnrollmentIn | None = None, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """学生退课。"""
    try:
        reason = req.drop_reason if req else None
        data = await EnrollmentService(db).drop_by_user(current_user.user_id, enrollment_id, drop_reason=reason)
        return api_success(data, message="Enrollment dropped successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/enrollments/{enrollment_id}/score")
async def update_enrollment_score(enrollment_id: int, req: ScoreUpdateIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """教师或管理员录入课程成绩。"""
    _require_staff(current_user)
    try:
        data = await EnrollmentService(db).update_score(enrollment_id, req.course_score)
        return api_success(data, message="Course score updated successfully")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
