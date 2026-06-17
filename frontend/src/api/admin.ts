import request from "./request";
import type { UserRole } from "./auth";

export interface AdminRoleCount {
  role: string;
  count: number;
}

export interface AdminDashboardStats {
  total_users: number;
  roles: AdminRoleCount[];
  course_count: number;
  class_count: number;
  question_count: number;
}

export interface RoleItem {
  role_id: number;
  role_name: UserRole | string;
}

export interface MenuItem {
  menu_id: number;
  menu_name: string;
  description?: string | null;
}

export interface PermissionItem {
  permission_id: number;
  permission_name: string;
  permission_code: string;
  description?: string | null;
}

export interface RolePermissionItem {
  id?: number;
  role_permission_id?: number;
  role_id: number;
  permission_id: number;
}

export interface PermissionMenuItem {
  id?: number;
  permission_menu_id?: number;
  permission_id: number;
  menu_id: number;
}

export const adminApi = {
  /** 后台首页统计 */
  getDashboardStats: () => request.get<AdminDashboardStats>("/admin/dashboard/stats"),

  /** 角色管理 */
  listRoles: () => request.get<RoleItem[]>("/admin/roles"),
  createRole: (role_name: string) => request.post<RoleItem>("/admin/roles", { role_name }),
  updateRole: (roleId: number, role_name: string) => request.patch<RoleItem>(`/admin/roles/${roleId}`, { role_name }),
  deleteRole: (roleId: number) => request.delete<boolean>(`/admin/roles/${roleId}`),
  assignRoleToUser: (payload: { user_id: number; role_name: string }) => request.post("/admin/user-roles", payload),

  /** 菜单管理 */
  listMenus: () => request.get<MenuItem[]>("/admin/menus"),
  createMenu: (payload: { menu_name: string; description?: string | null }) => request.post<MenuItem>("/admin/menus", payload),
  updateMenu: (menuId: number, payload: { menu_name?: string; description?: string | null }) => request.patch<MenuItem>(`/admin/menus/${menuId}`, payload),
  deleteMenu: (menuId: number) => request.delete<boolean>(`/admin/menus/${menuId}`),

  /** 权限管理 */
  listPermissions: () => request.get<PermissionItem[]>("/admin/permissions"),
  createPermission: (payload: { permission_name: string; permission_code: string; description?: string | null }) => request.post<PermissionItem>("/admin/permissions", payload),
  updatePermission: (permissionId: number, payload: { permission_name?: string; permission_code?: string; description?: string | null }) => request.patch<PermissionItem>(`/admin/permissions/${permissionId}`, payload),
  deletePermission: (permissionId: number) => request.delete<boolean>(`/admin/permissions/${permissionId}`),

  /** 角色-权限、权限-菜单绑定 */
  bindRolePermission: (payload: { role_id: number; permission_id: number }) => request.post<RolePermissionItem>("/admin/role-permissions", payload),
  listRolePermissions: (roleId: number) => request.get<RolePermissionItem[]>(`/admin/roles/${roleId}/permissions`),
  unbindRolePermission: (roleId: number, permissionId: number) => request.delete<boolean>(`/admin/roles/${roleId}/permissions/${permissionId}`),
  bindPermissionMenu: (payload: { permission_id: number; menu_id: number }) => request.post<PermissionMenuItem>("/admin/permission-menus", payload),
  unbindPermissionMenu: (permissionId: number, menuId: number) => request.delete<boolean>(`/admin/permissions/${permissionId}/menus/${menuId}`),
};
