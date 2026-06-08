from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.role import Role
from app.dao.userDao import UserDAO


"""
角色数据访问对象：
提供对角色表的增删改查操作，包括创建角色、根据ID查询角色、根据名称查询角色等功能。
角色DAO的主要职责包括：
1. 创建角色：根据用户ID和角色名称创建新的角色记录，并确保一个用户只能有一个角色。
2. 根据ID查询角色：根据角色ID查询角色的详细信息，包括角色名称和所属用户ID。
3. 根据名称查询角色：根据角色名称查询角色的详细信息，包括角色ID和所属用户ID。
4. 更新角色信息：根据角色ID更新角色的相关信息，例如修改角色名称等，并确保更新后的信息合理。
5. 删除角色：根据角色ID删除角色记录，实际操作为软删除，即将角色记录的状态标记为“deleted”，以保留历史数据。
"""
class RoleDAO:

    @staticmethod
    async def create_role(
        db: AsyncSession,
        role_name: str
    ):
        role = Role(
            role_name=role_name
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        return role
    
    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        role_name: str
    ):
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        return result.scalars().first()
   
