import { create } from "zustand";
import {
  adminApi,
  type AdminDashboardStats,
  type MenuItem,
  type PermissionItem,
  type PermissionMenuItem,
  type RoleItem,
  type RolePermissionItem,
} from "../api/admin";

/** 后台管理 Store：管理后台统计、角色、菜单、权限及绑定关系。 */
interface AdminStore {
  stats: AdminDashboardStats | null;
  roles: RoleItem[];
  menus: MenuItem[];
  permissions: PermissionItem[];
  rolePermissions: RolePermissionItem[];
  permissionMenuBindings: PermissionMenuItem[];
  loading: boolean;
  error: string | null;

  clearError: () => void;
  loadStats: () => Promise<AdminDashboardStats>;
  loadRoles: () => Promise<RoleItem[]>;
  createRole: (roleName: string) => Promise<RoleItem>;
  updateRole: (roleId: number, roleName: string) => Promise<RoleItem>;
  deleteRole: (roleId: number) => Promise<void>;
  assignRoleToUser: (payload: { user_id: number; role_name: string }) => Promise<unknown>;

  loadMenus: () => Promise<MenuItem[]>;
  createMenu: (payload: { menu_name: string; description?: string | null }) => Promise<MenuItem>;
  updateMenu: (menuId: number, payload: { menu_name?: string; description?: string | null }) => Promise<MenuItem>;
  deleteMenu: (menuId: number) => Promise<void>;

  loadPermissions: () => Promise<PermissionItem[]>;
  createPermission: (payload: { permission_name: string; permission_code: string; description?: string | null }) => Promise<PermissionItem>;
  updatePermission: (permissionId: number, payload: Partial<{ permission_name: string; permission_code: string; description: string | null }>) => Promise<PermissionItem>;
  deletePermission: (permissionId: number) => Promise<void>;

  loadRolePermissions: (roleId: number) => Promise<RolePermissionItem[]>;
  bindRolePermission: (payload: { role_id: number; permission_id: number }) => Promise<RolePermissionItem>;
  unbindRolePermission: (roleId: number, permissionId: number) => Promise<boolean>;

  bindPermissionMenu: (payload: { permission_id: number; menu_id: number }) => Promise<PermissionMenuItem>;
  unbindPermissionMenu: (permissionId: number, menuId: number) => Promise<boolean>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useAdminStore = create<AdminStore>((set) => ({
  stats: null,
  roles: [],
  menus: [],
  permissions: [],
  rolePermissions: [],
  permissionMenuBindings: [],
  loading: false,
  error: null,

  clearError: () => set({ error: null }),

  loadStats: async () => {
    set({ loading: true, error: null });
    try {
      const stats = await adminApi.getDashboardStats();
      set({ stats, loading: false });
      return stats;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载后台统计失败") });
      throw error;
    }
  },

  loadRoles: async () => {
    const roles = await adminApi.listRoles();
    set({ roles });
    return roles;
  },

  createRole: async (roleName) => {
    const role = await adminApi.createRole(roleName);
    set((state) => ({ roles: [role, ...state.roles] }));
    return role;
  },

  updateRole: async (roleId, roleName) => {
    const role = await adminApi.updateRole(roleId, roleName);
    set((state) => ({ roles: state.roles.map((item) => item.role_id === roleId ? role : item) }));
    return role;
  },

  deleteRole: async (roleId) => {
    await adminApi.deleteRole(roleId);
    set((state) => ({ roles: state.roles.filter((item) => item.role_id !== roleId) }));
  },

  assignRoleToUser: async (payload) => adminApi.assignRoleToUser(payload),

  loadMenus: async () => {
    const menus = await adminApi.listMenus();
    set({ menus });
    return menus;
  },

  createMenu: async (payload) => {
    const menu = await adminApi.createMenu(payload);
    set((state) => ({ menus: [menu, ...state.menus] }));
    return menu;
  },

  updateMenu: async (menuId, payload) => {
    const menu = await adminApi.updateMenu(menuId, payload);
    set((state) => ({ menus: state.menus.map((item) => item.menu_id === menuId ? menu : item) }));
    return menu;
  },

  deleteMenu: async (menuId) => {
    await adminApi.deleteMenu(menuId);
    set((state) => ({ menus: state.menus.filter((item) => item.menu_id !== menuId) }));
  },

  loadPermissions: async () => {
    const permissions = await adminApi.listPermissions();
    set({ permissions });
    return permissions;
  },

  createPermission: async (payload) => {
    const permission = await adminApi.createPermission(payload);
    set((state) => ({ permissions: [permission, ...state.permissions] }));
    return permission;
  },

  updatePermission: async (permissionId, payload) => {
    const permission = await adminApi.updatePermission(permissionId, payload);
    set((state) => ({ permissions: state.permissions.map((item) => item.permission_id === permissionId ? permission : item) }));
    return permission;
  },

  deletePermission: async (permissionId) => {
    await adminApi.deletePermission(permissionId);
    set((state) => ({ permissions: state.permissions.filter((item) => item.permission_id !== permissionId) }));
  },

  loadRolePermissions: async (roleId) => {
    const rolePermissions = await adminApi.listRolePermissions(roleId);
    set({ rolePermissions });
    return rolePermissions;
  },

  bindRolePermission: async (payload) => {
    const rolePermission = await adminApi.bindRolePermission(payload);
    set((state) => ({ rolePermissions: [rolePermission, ...state.rolePermissions] }));
    return rolePermission;
  },

  unbindRolePermission: async (roleId, permissionId) => {
    const success = await adminApi.unbindRolePermission(roleId, permissionId);
    set((state) => ({ rolePermissions: state.rolePermissions.filter((item) => item.permission_id !== permissionId) }));
    return success;
  },

  bindPermissionMenu: async (payload) => {
    const permissionMenu = await adminApi.bindPermissionMenu(payload);
    set((state) => ({ permissionMenuBindings: [permissionMenu, ...state.permissionMenuBindings] }));
    return permissionMenu;
  },

  unbindPermissionMenu: async (permissionId, menuId) => {
    const success = await adminApi.unbindPermissionMenu(permissionId, menuId);
    set((state) => ({ permissionMenuBindings: state.permissionMenuBindings.filter((item) => !(item.permission_id === permissionId && item.menu_id === menuId)) }));
    return success;
  },
}));
