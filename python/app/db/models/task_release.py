from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class TaskRelease(Base):
    __tablename__ = "task_releases"

    task_publish_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task_bank.task_id"), nullable=False, index=True)
    publish_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deadline = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
