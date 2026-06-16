import request, { type ApiResponse } from "./request";

export type UserRole = "admin" | "teacher" | "student";
export type UserStatus = "active" | "inactive" | "deleted";

/** 用户基础信息。后端不返回 pwd。 */
export interface User {
  user_id?: number;
  id?: number;
  username: string;
  email?: string | null;
  avatar?: string | null;
  role: UserRole;
  status?: UserStatus;
  created_at?: string;
  updated_at?: string;
}

export interface LoginParams {
  username: string;
  pwd: string;
  role?: UserRole;
}

export interface RegisterParams {
  username: string;
  pwd: string;
  role?: UserRole;
  email?: string | null;
  avatar?: string | null;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface UserProfileUpdateParams {
  username?: string;
  email?: string | null;
  avatar?: string | null;
}

export interface ChangePasswordParams {
  old_password: string;
  new_password: string;
}

/** 登录：POST /auth/login */
export const login = (params: LoginParams): Promise<LoginResponse> =>
  request.post("/auth/login", params);

/** 注册：POST /auth/register */
export const register = (params: RegisterParams): Promise<User> =>
  request.post("/auth/register", params);

/** 当前登录用户：GET /auth/me */
export const fetchCurrentUser = (): Promise<User> => request.get("/auth/me");

/** 指定用户信息：GET /auth/info/{user_id} */
export const fetchUserInfo = (userId: number): Promise<User> =>
  request.get(`/auth/info/${userId}`);

/** 更新用户基础资料：PATCH /auth/info/{user_id} */
export const updateUserInfo = (
  userId: number,
  params: UserProfileUpdateParams
): Promise<User> => request.patch(`/auth/info/${userId}`, params);

/** 修改当前用户密码：POST /auth/change-password */
export const changeAuthPassword = (params: ChangePasswordParams): Promise<boolean> =>
  request.post("/auth/change-password", params);

/** 管理员更新用户状态：PATCH /auth/status/{user_id} */
export const updateUserStatus = (userId: number, status: UserStatus): Promise<boolean> =>
  request.patch(`/auth/status/${userId}`, { status });

/** 退出登录：JWT 无状态，前端清理 token 即可。 */
export const logout = (): Promise<null> => request.post("/auth/logout");

/**
 * 兼容旧代码导入。当前后端 router 没有 /auth/refresh，业务上不应调用。
 */
export const refreshToken = (): Promise<{ token: string }> =>
  Promise.reject(new Error("当前后端未提供 /auth/refresh 接口"));

export type { ApiResponse };
