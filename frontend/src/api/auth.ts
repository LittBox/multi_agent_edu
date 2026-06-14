import request, { type ApiResponse } from './request.ts';

export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'teacher' | 'student';
}

export interface LoginParams {
  username: string;
  pwd: string;
  role?: 'admin' | 'teacher' | 'student';
}

export interface LoginResponse {
  token: string;
  user: User;
}

export const login = (params: LoginParams): Promise<LoginResponse> => {
  return request.post('/auth/login', params);
};

export const logout = (): Promise<ApiResponse<null>> => {
  return request.post('/auth/logout');
};

export const fetchCurrentUser = (): Promise<User> => {
  return request.get('/auth/me');
};

export const refreshToken = (): Promise<{ token: string }> => {
  return request.post('/auth/refresh');
};

export const register = (params: LoginParams) => {
  return request.post('/auth/register', params);
};
