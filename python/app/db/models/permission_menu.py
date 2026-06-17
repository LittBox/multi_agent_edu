from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from app.db.database import Base


class PermissionMenu(Base):
    __tablename__ = "permission_menus"

    id = Column(Integer, primary_key=True, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.permission_id"), nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("menus.menu_id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("permission_id", "menu_id", name="uq_permission_menu"),
    )
