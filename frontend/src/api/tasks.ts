import request from "./request";

export interface TaskReleaseItem {
  task_publish_id: number;
  task_id: number;
  publish_time: string;
  deadline?: string | null;
  is_deleted?: number;
  task_content?: string | null;
  task_type?: string | null;
  course_id?: number | null;
}

export interface TaskSubmissionItem {
  submit_id: number;
  task_publish_id: number;
  student_id: number;
  submit_time: string;
  answer_content: string;
  score?: number | null;
  comment?: string | null;
}

export interface TaskBankItem {
  task_id: number;
  course_id: number;
  teacher_id: number;
  task_type: string;
  task_content: string;
  is_deleted?: number;
  created_at: string;
  updated_at: string;
}

export interface TaskBankCreatePayload {
  course_id: number;
  task_type?: string;
  task_content: string;
}

export interface TaskBankUpdatePayload {
  course_id?: number;
  teacher_id?: number;
  task_type?: string;
  task_content?: string;
}

export interface TaskReleasePayload {
  task_id: number;
  deadline?: string | null;
}

export interface TaskReleaseUpdatePayload {
  deadline?: string | null;
  is_deleted?: number;
}

export const taskApi = {
  /** GET /tasks/bank：教师/管理员查看作业题库 */
  listBank: (params?: { course_id?: number; teacher_id?: number }) =>
    request.get<TaskBankItem[]>("/tasks/bank", { params }),

  /** POST /tasks/bank：创建作业题库条目 */
  createBank: (payload: TaskBankCreatePayload) => request.post<TaskBankItem>("/tasks/bank", payload),

  /** PATCH /tasks/bank/{task_id}：更新作业题库条目 */
  updateBank: (taskId: number, payload: TaskBankUpdatePayload) => request.patch<TaskBankItem>(`/tasks/bank/${taskId}`, payload),

  /** DELETE /tasks/bank/{task_id}：删除作业题库条目 */
  deleteBank: (taskId: number) => request.delete<boolean>(`/tasks/bank/${taskId}`),

  /** 兼容旧题库命名：GET /tasks/questions */
  listQuestions: () => request.get<TaskBankItem[]>("/tasks/questions"),

  /** POST /tasks/questions：兼容旧作业题库创建入口 */
  createQuestion: (payload: TaskBankCreatePayload) => request.post<TaskBankItem>("/tasks/questions", payload),

  /** POST /tasks/releases：发布作业 */
  release: (payload: TaskReleasePayload) => request.post<TaskReleaseItem>("/tasks/releases", payload),

  /** GET /tasks/releases：已发布作业 */
  listReleases: () => request.get<TaskReleaseItem[]>("/tasks/releases"),

  /** PATCH /tasks/releases/{task_publish_id}：更新作业发布信息 */
  updateRelease: (taskPublishId: number, payload: TaskReleaseUpdatePayload) =>
    request.patch<TaskReleaseItem>(`/tasks/releases/${taskPublishId}`, payload),

  /** DELETE /tasks/releases/{task_publish_id}：删除作业发布 */
  deleteRelease: (taskPublishId: number) => request.delete<boolean>(`/tasks/releases/${taskPublishId}`),

  /** POST /tasks/releases/{task_publish_id}/submit：学生提交作业 */
  submit: (taskPublishId: number, answer_content: string) =>
    request.post<TaskSubmissionItem>(`/tasks/releases/${taskPublishId}/submit`, { answer_content }),

  /** GET /tasks/submissions/me：我的提交记录 */
  mySubmissions: () => request.get<TaskSubmissionItem[]>("/tasks/submissions/me"),

  /** PUT /tasks/submissions/{submit_id}/grade：教师批改 */
  grade: (submitId: number, payload: { score: number; comment?: string | null }) =>
    request.put<TaskSubmissionItem>(`/tasks/submissions/${submitId}/grade`, payload),
  
  /** GET /tasks/releases/{task_publish_id}/submissions：教师查看某次发布作业的提交列表 */
  submissions: (taskPublishId: number) => 
    request.get<TaskSubmissionItem[]>(`/tasks/releases/${taskPublishId}/submit`),
};
