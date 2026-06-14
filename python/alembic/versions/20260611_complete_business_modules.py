"""Complete task exam permission modules.

Revision ID: 20260611_complete_business_modules
Revises: 20260607_unify_contact_fields
Create Date: 2026-06-11 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision = "20260611_complete_business_modules"
down_revision = "20260607_unify_contact_fields"
branch_labels = None
depends_on = None


def _tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    tables = _tables()

    if "course_enrollments" in tables and "course_score" not in _columns("course_enrollments"):
        op.add_column("course_enrollments", sa.Column("course_score", sa.Float(), nullable=True))
    if "knowledge_points" in tables and "course_id" not in _columns("knowledge_points"):
        op.add_column("knowledge_points", sa.Column("course_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_knowledge_points_course_id", "knowledge_points", "courses", ["course_id"], ["course_id"])
    if "questions" in tables and "course_id" not in _columns("questions"):
        op.add_column("questions", sa.Column("course_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_questions_course_id", "questions", "courses", ["course_id"], ["course_id"])

    if "task_bank" not in tables:
        op.create_table(
            "task_bank",
            sa.Column("task_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.course_id"), nullable=False),
            sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("teachers.teacher_id"), nullable=False),
            sa.Column("task_type", sa.String(length=30), nullable=False, server_default="homework"),
            sa.Column("task_content", sa.Text(), nullable=False),
            sa.Column("is_deleted", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "task_releases" not in tables:
        op.create_table(
            "task_releases",
            sa.Column("task_publish_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("task_id", sa.Integer(), sa.ForeignKey("task_bank.task_id"), nullable=False),
            sa.Column("publish_time", sa.DateTime(timezone=True), nullable=False),
            sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_deleted", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "task_submissions" not in tables:
        op.create_table(
            "task_submissions",
            sa.Column("submit_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("task_publish_id", sa.Integer(), sa.ForeignKey("task_releases.task_publish_id"), nullable=False),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.student_id"), nullable=False),
            sa.Column("submit_time", sa.DateTime(timezone=True), nullable=False),
            sa.Column("answer_content", sa.Text(), nullable=False),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("task_publish_id", "student_id", name="uq_task_submission_student"),
        )

    if "exams" not in tables:
        op.create_table(
            "exams",
            sa.Column("exam_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("course_id", sa.Integer(), sa.ForeignKey("courses.course_id"), nullable=False),
            sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("teachers.teacher_id"), nullable=False),
            sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="60"),
            sa.Column("exam_type", sa.String(length=30), nullable=False, server_default="quiz"),
            sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
            sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
            sa.Column("is_deleted", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
    if "exam_questions" not in tables:
        op.create_table(
            "exam_questions",
            sa.Column("exam_question_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("exam_id", sa.Integer(), sa.ForeignKey("exams.exam_id"), nullable=False),
            sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.question_id"), nullable=False),
            sa.Column("score", sa.Float(), nullable=False, server_default="10"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),
        )
    if "exam_submits" not in tables:
        op.create_table(
            "exam_submits",
            sa.Column("exam_submit_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("exam_id", sa.Integer(), sa.ForeignKey("exams.exam_id"), nullable=False),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.student_id"), nullable=False),
            sa.Column("submit_time", sa.DateTime(timezone=True), nullable=False),
            sa.Column("total_score", sa.Float(), nullable=True),
            sa.Column("teacher_comment", sa.Text(), nullable=True),
            sa.Column("answers_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("exam_id", "student_id", name="uq_exam_submit_student"),
        )

    if "permissions" not in tables:
        op.create_table(
            "permissions",
            sa.Column("permission_id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("permission_name", sa.String(length=100), nullable=False),
            sa.Column("permission_code", sa.String(length=100), nullable=False, unique=True),
            sa.Column("description", sa.Text(), nullable=True),
        )
    if "role_permissions" not in tables:
        op.create_table(
            "role_permissions",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.role_id"), nullable=False),
            sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.permission_id"), nullable=False),
            sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        )
    if "permission_menus" not in tables:
        op.create_table(
            "permission_menus",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.permission_id"), nullable=False),
            sa.Column("menu_id", sa.Integer(), sa.ForeignKey("menus.menu_id"), nullable=False),
            sa.UniqueConstraint("permission_id", "menu_id", name="uq_permission_menu"),
        )


def downgrade() -> None:
    for table_name in ("permission_menus", "role_permissions", "permissions", "exam_submits", "exam_questions", "exams", "task_submissions", "task_releases", "task_bank"):
        if table_name in _tables():
            op.drop_table(table_name)
