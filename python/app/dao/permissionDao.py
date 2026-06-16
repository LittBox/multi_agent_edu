from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.menu import Menu
from app.db.models.permission import Permission, PermissionMenu, RolePermission
from app.db.models.role import Role

"""
权限 DAO。
包含 PermissionDAO、RolePermissionDAO、PermissionMenuDAO。
对应 permissions、role_permissions、permission_menus 三张表。
"""

class PermissionDAO:
    @staticmethod
    async def create_permission(db: AsyncSession, permission_name: str, permission_code: str,
                                description: str | None = None) -> Permission:
        permission = Permission(permission_name=permission_name, permission_code=permission_code, description=description)
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission

    @staticmethod
    async def get_by_id(db: AsyncSession, permission_id: int) -> Permission | None:
        result = await db.execute(select(Permission).where(Permission.permission_id == permission_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_code(db: AsyncSession, permission_code: str) -> Permission | None:
        result = await db.execute(select(Permission).where(Permission.permission_code == permission_code))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Permission]:
        result = await db.execute(select(Permission).order_by(Permission.permission_id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def update_permission(db: AsyncSession, permission_id: int, permission_name: str | None = None,
                                permission_code: str | None = None, description: str | None = None) -> Permission | None:
        permission = await PermissionDAO.get_by_id(db, permission_id)
        if not permission:
            return None
        if permission_name is not None:
            permission.permission_name = permission_name
        if permission_code is not None:
            permission.permission_code = permission_code
        if description is not None:
            permission.description = description
        await db.commit()
        await db.refresh(permission)
        return permission

    @staticmethod
    async def delete_permission(db: AsyncSession, permission_id: int) -> bool:
        permission = await PermissionDAO.get_by_id(db, permission_id)
        if not permission:
            return False
        await db.delete(permission)
        await db.commit()
        return True


class RolePermissionDAO:
    @staticmethod
    async def assign_permission(db: AsyncSession, role_id: int, permission_id: int) -> RolePermission:
        existed = await RolePermissionDAO.get_by_role_permission(db, role_id, permission_id)
        if existed:
            return existed
        relation = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(relation)
        await db.commit()
        await db.refresh(relation)
        return relation

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> RolePermission | None:
        result = await db.execute(select(RolePermission).where(RolePermission.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_role_permission(db: AsyncSession, role_id: int, permission_id: int) -> RolePermission | None:
        result = await db.execute(select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_role_id(db: AsyncSession, role_id: int) -> list[RolePermission]:
        result = await db.execute(select(RolePermission).where(RolePermission.role_id == role_id).order_by(RolePermission.id.asc()))
        return list(result.scalars().all())

    @staticmethod
    async def get_permissions_by_role(db: AsyncSession, role_id: int) -> list[Permission]:
        result = await db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
            .where(RolePermission.role_id == role_id)
            .order_by(Permission.permission_id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_roles_by_permission(db: AsyncSession, permission_id: int) -> list[Role]:
        result = await db.execute(
            select(Role)
            .join(RolePermission, RolePermission.role_id == Role.role_id)
            .where(RolePermission.permission_id == permission_id)
            .order_by(Role.role_id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def has_permission(db: AsyncSession, role_id: int, permission_code: str) -> bool:
        result = await db.execute(
            select(RolePermission)
            .join(Permission, Permission.permission_id == RolePermission.permission_id)
            .where(RolePermission.role_id == role_id, Permission.permission_code == permission_code)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def remove_permission(db: AsyncSession, role_id: int, permission_id: int) -> bool:
        relation = await RolePermissionDAO.get_by_role_permission(db, role_id, permission_id)
        if not relation:
            return False
        await db.delete(relation)
        await db.commit()
        return True


class PermissionMenuDAO:
    @staticmethod
    async def bind_permission_menu(db: AsyncSession, permission_id: int, menu_id: int) -> PermissionMenu:
        existed = await PermissionMenuDAO.get_by_permission_menu(db, permission_id, menu_id)
        if existed:
            return existed
        relation = PermissionMenu(permission_id=permission_id, menu_id=menu_id)
        db.add(relation)
        await db.commit()
        await db.refresh(relation)
        return relation

    @staticmethod
    async def get_by_id(db: AsyncSession, id: int) -> PermissionMenu | None:
        result = await db.execute(select(PermissionMenu).where(PermissionMenu.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_permission_menu(db: AsyncSession, permission_id: int, menu_id: int) -> PermissionMenu | None:
        result = await db.execute(select(PermissionMenu).where(
            PermissionMenu.permission_id == permission_id,
            PermissionMenu.menu_id == menu_id,
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_menus_by_permission(db: AsyncSession, permission_id: int) -> list[Menu]:
        result = await db.execute(
            select(Menu)
            .join(PermissionMenu, PermissionMenu.menu_id == Menu.menu_id)
            .where(PermissionMenu.permission_id == permission_id)
            .order_by(Menu.menu_id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def remove_permission_menu(db: AsyncSession, permission_id: int, menu_id: int) -> bool:
        relation = await PermissionMenuDAO.get_by_permission_menu(db, permission_id, menu_id)
        if not relation:
            return False
        await db.delete(relation)
        await db.commit()
        return True
