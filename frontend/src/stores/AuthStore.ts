import { create } from "zustand";
import {
  login as apiLogin,
  logout as apiLogout,
  fetchCurrentUser,
  register as apiRegister,
  updateUserInfo,
  type LoginParams,
  type RegisterParams,
  type User,
  type UserRole,
  type UserProfileUpdateParams,
} from "../api/auth";

/**
 * 登录页面状态。
 * carousel：首页轮播/欢迎页；login：登录页；home：业务主页。
 */
type AuthPageState = "carousel" | "login" | "home";

/**
 * 认证状态管理。
 * 负责保存当前登录用户、登录态初始化、登录、注册、退出和当前用户资料刷新。
 */
interface AuthStore {
  page: AuthPageState;
  user: User | null;
  loading: boolean;
  error: string | null;

  goCarousel: () => void;
  goLogin: () => void;
  goHome: () => void;
  clearError: () => void;

  initAuth: () => Promise<void>;
  login: (username: string, pwd: string, role?: UserRole) => Promise<void>;
  loginWithPayload: (params: LoginParams) => Promise<void>;
  register: (params: RegisterParams) => Promise<User>;
  refreshCurrentUser: () => Promise<User | null>;
  updateCurrentUser: (params: UserProfileUpdateParams) => Promise<User>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  page: "carousel",
  user: null,
  loading: true,
  error: null,

  goCarousel: () => set({ page: "carousel" }),
  goLogin: () => set({ page: "login" }),
  goHome: () => set({ page: "home" }),
  clearError: () => set({ error: null }),

  /**
   * 页面启动时调用：
   * 1. 本地没有 token：直接回到欢迎页。
   * 2. 本地有 token：请求 /auth/me 校验 token 并恢复用户信息。
   */
  initAuth: async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      set({ user: null, page: "carousel", loading: false, error: null });
      return;
    }

    set({ loading: true, error: null });
    try {
      const user = await fetchCurrentUser();
      set({ user, page: "home", loading: false, error: null });
    } catch (error) {
      localStorage.removeItem("accessToken");
      set({
        user: null,
        page: "carousel",
        loading: false,
        error: error instanceof Error ? error.message : "登录状态已失效",
      });
    }
  },

  /** 登录：后端返回 token 后写入 localStorage，再保存用户信息。 */
  login: async (username, pwd, role) => {
    await get().loginWithPayload({ username, pwd, role });
  },

  loginWithPayload: async (params) => {
    set({ loading: true, error: null });
    try {
      const { token, user } = await apiLogin(params);
      localStorage.setItem("accessToken", token);
      set({ user, page: "home", loading: false, error: null });
    } catch (error) {
      set({ loading: false, error: error instanceof Error ? error.message : "登录失败" });
      throw error;
    }
  },

  /** 注册：创建用户后返回用户信息；是否自动登录由页面决定。 */
  register: async (params) => {
    set({ loading: true, error: null });
    try {
      const user = await apiRegister(params);
      set({ loading: false, error: null });
      return user;
    } catch (error) {
      set({ loading: false, error: error instanceof Error ? error.message : "注册失败" });
      throw error;
    }
  },

  /** 重新拉取当前登录用户信息，用于刷新头像、邮箱、角色等。 */
  refreshCurrentUser: async () => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      set({ user: null, page: "carousel", loading: false });
      return null;
    }

    try {
      const user = await fetchCurrentUser();
      set({ user, page: "home", error: null });
      return user;
    } catch (error) {
      localStorage.removeItem("accessToken");
      set({ user: null, page: "carousel", error: error instanceof Error ? error.message : "用户信息刷新失败" });
      return null;
    }
  },

  /** 更新当前用户基础资料。 */
  updateCurrentUser: async (params) => {
    const current = get().user;
    if (!current) {
      throw new Error("当前未登录");
    }
    const updated = await updateUserInfo(current.user_id, params);
    set({ user: updated, error: null });
    return updated;
  },

  /** 退出登录：后端 JWT 是无状态的，核心动作是清理本地 token 和用户信息。 */
  logout: async () => {
    try {
      await apiLogout();
    } finally {
      localStorage.removeItem("accessToken");
      set({ user: null, page: "carousel", loading: false, error: null });
    }
  },
}));
