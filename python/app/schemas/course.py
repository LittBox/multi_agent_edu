from pydantic import BaseModel
from typing import Optional


class CourseCreate(BaseModel):
    course_code: str
    course_name: str
    credit: float
    description: Optional[str] = None
    teacher_id: int


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credit: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CourseResponse(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    credit: float
    description: Optional[str]
    created_by_teacher_id: int
    status: str

    class Config:
        from_attributes = True
