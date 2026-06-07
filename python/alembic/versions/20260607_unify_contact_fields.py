"""Unify contact fields onto users table.

Revision ID: 20260607_unify_contact_fields
Revises: None
Create Date: 2026-06-07 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision = "20260607_unify_contact_fields"
down_revision = None
branch_labels = None
depends_on = None


def _table_names(inspector) -> set[str]:
    return set(inspector.get_table_names())


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _copy_contact_values(bind, source_table_name: str) -> None:
    inspector = inspect(bind)
    table_names = _table_names(inspector)
    if "users" not in table_names or source_table_name not in table_names:
        return

    source_columns = _column_names(inspector, source_table_name)
    contact_columns = [column for column in ("email", "phone") if column in source_columns]
    if not contact_columns:
        return

    metadata = sa.MetaData()
    users = sa.Table("users", metadata, autoload_with=bind)
    source = sa.Table(source_table_name, metadata, autoload_with=bind)

    rows = bind.execute(
        sa.select(source.c.user_id, *[source.c[column] for column in contact_columns])
    ).mappings().all()

    for row in rows:
        current_user = bind.execute(
            sa.select(users.c.email, users.c.phone).where(users.c.user_id == row["user_id"])
        ).mappings().first()
        if current_user is None:
            continue

        updates: dict[str, str] = {}
        if "email" in contact_columns and current_user["email"] is None and row["email"] is not None:
            updates["email"] = row["email"]
        if "phone" in contact_columns and current_user["phone"] is None and row["phone"] is not None:
            updates["phone"] = row["phone"]

        if updates:
            bind.execute(
                sa.update(users).where(users.c.user_id == row["user_id"]).values(**updates)
            )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    table_names = _table_names(inspector)

    if "users" in table_names:
        user_columns = _column_names(inspector, "users")
        if "phone" not in user_columns:
            op.add_column(
                "users",
                sa.Column("phone", sa.String(length=20), nullable=True),
            )

    if "students" in table_names:
        _copy_contact_values(bind, "students")
        student_columns = _column_names(inspector, "students")
        with op.batch_alter_table("students") as batch_op:
            if "phone" in student_columns:
                batch_op.drop_column("phone")
            if "email" in student_columns:
                batch_op.drop_column("email")

    if "teachers" in table_names:
        _copy_contact_values(bind, "teachers")
        teacher_columns = _column_names(inspector, "teachers")
        with op.batch_alter_table("teachers") as batch_op:
            if "phone" in teacher_columns:
                batch_op.drop_column("phone")
            if "email" in teacher_columns:
                batch_op.drop_column("email")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    table_names = _table_names(inspector)

    if "students" in table_names:
        student_columns = _column_names(inspector, "students")
        with op.batch_alter_table("students") as batch_op:
            if "phone" not in student_columns:
                batch_op.add_column(
                    sa.Column("phone", sa.String(length=20), nullable=True),
                )
            if "email" not in student_columns:
                batch_op.add_column(
                    sa.Column("email", sa.String(length=100), nullable=True),
                )

    if "teachers" in table_names:
        teacher_columns = _column_names(inspector, "teachers")
        with op.batch_alter_table("teachers") as batch_op:
            if "phone" not in teacher_columns:
                batch_op.add_column(
                    sa.Column("phone", sa.String(length=20), nullable=True),
                )
            if "email" not in teacher_columns:
                batch_op.add_column(
                    sa.Column("email", sa.String(length=100), nullable=True),
                )

    if "users" in table_names:
        user_columns = _column_names(inspector, "users")
        if "phone" in user_columns:
            op.drop_column("users", "phone")
