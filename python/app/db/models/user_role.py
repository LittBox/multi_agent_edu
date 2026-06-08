from app.db.base import Base
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


"""
用户角色关联表
"""
class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    #这里的users.user_id里的users是数据库的表名，而不是模型类名User。因为在定义User模型时，__tablename__属性被设置为"users"，所以在ForeignKey中引用时需要使用表名而不是模型类名。
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)

    #对象层级关系映射，通过relationship函数建立与User模型的关系，使得在查询UserRole对象时，可以方便地访问关联的User对象
    user = relationship("User")
    role = relationship("Role")