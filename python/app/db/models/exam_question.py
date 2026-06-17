from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint

from app.db.database import Base


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    exam_question_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.question_id"), nullable=False, index=True)
    score = Column(Float, nullable=False, default=10)
    sort_order = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),
    )
