from pydantic import BaseModel
from typing import Optional


class TeacherCreate(BaseModel):
    user_id: int
    teacher_no: str
    teacher_name: str
    department: Optional[str] = None
    title: Optional[str] = None


class TeacherUpdate(BaseModel):
    teacher_name: Optional[str] = None
    department: Optional[str] = None
    title: Optional[str] = None


class TeacherResponse(BaseModel):
    teacher_id: int
    user_id: int
    teacher_no: str
    teacher_name: str
    department: Optional[str]
    title: Optional[str]

    class Config:
        from_attributes = True
