from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from app.db.database import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.permission_id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
