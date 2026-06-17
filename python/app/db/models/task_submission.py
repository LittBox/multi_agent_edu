from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class TaskSubmission(Base):
    __tablename__ = "task_submissions"

    submit_id = Column(Integer, primary_key=True, index=True)
    task_publish_id = Column(Integer, ForeignKey("task_releases.task_publish_id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    submit_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    answer_content = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("task_publish_id", "student_id", name="uq_task_submission_student"),
    )
