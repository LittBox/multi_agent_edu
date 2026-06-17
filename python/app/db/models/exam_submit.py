from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class ExamSubmit(Base):
    __tablename__ = "exam_submits"

    exam_submit_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    submit_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    total_score = Column(Float, nullable=True)
    teacher_comment = Column(Text, nullable=True)
    answers_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_exam_submit_student"),
    )
