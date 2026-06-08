from app.db.base import Base
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


"""
角色表，记录系统中的角色信息，包括角色名称、所属用户等
"""
class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(20), nullable=False)