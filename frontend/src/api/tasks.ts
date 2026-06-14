import request from "./request";

export interface TaskReleaseItem {
  task_publish_id: number;
  task_id: number;
  publish_time: string;
  deadline?: string | null;
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
  created_at: string;
  updated_at: string;
}

export const taskApi = {
  listBank: () => request.get<TaskBankItem[]>("/v1/tasks/bank"),
  createBank: (payload: { course_id: number; task_type: string; task_content: string }) =>
    request.post<TaskBankItem>("/v1/tasks/bank", payload),
  release: (payload: { task_id: number; deadline?: string | null }) =>
    request.post<TaskReleaseItem>("/v1/tasks/releases", payload),
  listReleases: () => request.get<TaskReleaseItem[]>("/v1/tasks/releases"),
  submit: (taskPublishId: number, answer_content: string) =>
    request.post<TaskSubmissionItem>(`/v1/tasks/releases/${taskPublishId}/submit`, { answer_content }),
  mySubmissions: () => request.get<TaskSubmissionItem[]>("/v1/tasks/submissions/me"),
  submissions: (taskPublishId: number) =>
    request.get<TaskSubmissionItem[]>(`/v1/tasks/releases/${taskPublishId}/submissions`),
  grade: (submitId: number, payload: { score: number; comment?: string | null }) =>
    request.put<TaskSubmissionItem>(`/v1/tasks/submissions/${submitId}/grade`, payload),
};
