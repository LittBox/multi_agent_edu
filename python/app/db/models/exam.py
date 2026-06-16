from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Exam(Base):
    """
    考试表。

    记录考试基本信息，包括考试标题、所属课程、出题教师、考试时长、考试时间和状态。
    """

    __tablename__ = "exams"

    # 考试主键，自增。
    exam_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 考试标题。
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # 所属课程。
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.course_id"), nullable=False)

    # 发布考试的教师。
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.teacher_id"), nullable=False)

    # 考试时长，单位分钟。
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    # 考试类型，例如 quiz、midterm、final。
    exam_type: Mapped[str] = mapped_column(String(30), nullable=False, default="quiz")

    # 开始时间。
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 结束时间。
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 考试状态，示例数据里使用了 published。
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")

    # 软删除标记：0 表示正常，1 表示删除。
    is_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    course = relationship("Course", back_populates="exams")
    teacher = relationship("Teacher", back_populates="exams")

    # 考试包含的题目。
    exam_questions = relationship("ExamQuestion", back_populates="exam")

    # 学生提交记录。
    exam_submits = relationship("ExamSubmit", back_populates="exam")

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_exam_duration_positive"),
        CheckConstraint("status IN ('draft', 'published', 'closed', 'finished')", name="ck_exam_status"),
    )


class ExamQuestion(Base):
    """
    考试题目关联表。

    表示某场考试包含哪些题目，以及每道题的分值和排序。
    """

    __tablename__ = "exam_questions"

    # 考试题目关联主键，自增。
    exam_question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 考试 ID。
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.exam_id"), nullable=False)

    # 题目 ID。
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.question_id"), nullable=False)

    # 该题在考试中的分值。
    score: Mapped[float] = mapped_column(Float, nullable=False, default=10)

    # 题目排序，数字越小越靠前。
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    exam = relationship("Exam", back_populates="exam_questions")
    question = relationship("Question", back_populates="exam_questions")

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),
    )


class ExamSubmit(Base):
    """
    考试提交表。

    记录学生参加某场考试后的提交结果、总分、教师评语和答案详情。
    """

    __tablename__ = "exam_submits"

    # 考试提交主键，自增。
    exam_submit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 考试 ID。
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.exam_id"), nullable=False)

    # 学生 ID。
    student_id: Mapped[int] = mapped_column(ForeignKey("students.student_id"), nullable=False)

    # 提交时间。
    submit_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # 总分。
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 教师评语。
    teacher_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 学生答案详情，JSONB 格式。
    answers_json: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    exam = relationship("Exam", back_populates="exam_submits")
    student = relationship("Student", back_populates="exam_submits")

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_exam_submit_student"),
    )
