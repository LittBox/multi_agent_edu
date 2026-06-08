from app.db.base import Base
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

class RoleMenu(Base):
    __tablename__ = "role_menus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.menu_id"), nullable=False)

    role = relationship("Role")
    menu = relationship("Menu")
