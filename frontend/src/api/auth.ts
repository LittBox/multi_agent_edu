// src/api/auth.ts
import request, { type ApiResponse } from './request.ts'; // 假设已封装的 axios 实例

// ---------- 类型定义 ----------
export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  role: 'user' | 'admin';
}

export interface LoginParams {
  username: string;
  pwd: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

// ---------- API 函数 ----------

/**
 * 用户登录
 * @param params 登录参数
 * @returns Promise<LoginResponse>
 */
export const login = (params: LoginParams): Promise<LoginResponse> => {
  return request.post('/auth/login', params);
};

/**
 * 用户登出
 */
export const logout = (): Promise<ApiResponse<null>> => {
  return request.post('/auth/logout');
};

/**
 * 获取当前登录用户信息（用于验证 token 并恢复登录态）
 * @returns Promise<User>
 */
export const fetchCurrentUser = (): Promise<User> => {
  return request.get('/auth/me');
};

/**
 * 刷新 token（可选）
 */
export const refreshToken = (): Promise<{ token: string }> => {
  return request.post('/auth/refresh');
};

export const register = (params: LoginParams) => {
  return request.post("/auth/register", params);
};