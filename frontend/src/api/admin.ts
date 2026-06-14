import request from "./request";

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

export const adminApi = {
  getDashboardStats: () =>
    request.get<AdminDashboardStats>("/admin/dashboard/stats"),
};
