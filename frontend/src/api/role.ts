import request from "./request";

export interface StudentRoleUser {
  user_id: number;
  username: string;
  email?: string | null;
  role_name: string;

  student_id?: number | null;
  student_no?: string | null;
  student_name?: string | null;
  major?: string | null;
  grade?: number | null;
  class_name?: string | null;
}

export interface StudentInfoUpdatePayload {
  student_no?: string | null;
  student_name?: string | null;
  major?: string | null;
  grade?: number | null;
  class_name?: string | null;
}

export const roleApi = {
  /** GET /roles/students/me：获取当前登录学生资料 */
  getMyStudentInfo: (): Promise<StudentRoleUser> =>
    request.get("/roles/students/me"),

  /** PATCH /roles/students/me：更新当前登录学生资料 */
  updateMyStudentInfo: (
    payload: StudentInfoUpdatePayload
  ): Promise<StudentRoleUser> =>
    request.patch("/roles/students/me", payload),
};