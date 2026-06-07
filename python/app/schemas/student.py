from pydantic import BaseModel
from typing import Optional


class StudentCreate(BaseModel):
    user_id: int
    student_no: str
    student_name: str
    major: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None


class StudentUpdate(BaseModel):
    student_name: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None


class StudentResponse(BaseModel):
    student_id: int
    user_id: int
    student_no: str
    student_name: str
    major: Optional[str]
    grade: Optional[int]
    class_name: Optional[str]

    class Config:
        from_attributes = True
