import request from "./request";

export interface ExamItem {
  exam_id: number;
  title: string;
  course_id: number;
  teacher_id: number;
  duration_minutes: number;
  exam_type: string;
  status: string;
  start_time?: string | null;
  end_time?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface ExamCreatePayload {
  title: string;
  course_id: number;
  duration_minutes?: number;
  exam_type?: string;
  start_time?: string | null;
  end_time?: string | null;
  status?: string;
}

export type ExamUpdatePayload = Partial<ExamCreatePayload> & { teacher_id?: number };

export interface ExamQuestionItem {
  exam_question_id: number;
  exam_id: number;
  question_id: number;
  score: number;
  sort_order: number;
  stem?: string | null;
  question_type?: string | null;
  option_a?: string | null;
  option_b?: string | null;
  option_c?: string | null;
  option_d?: string | null;
}

export interface ExamQuestionPayload {
  question_id: number;
  score?: number;
  sort_order?: number;
}

export interface ExamDetail extends ExamItem {
  questions: ExamQuestionItem[];
  server_time?: string;
}

export interface ExamSubmissionItem {
  exam_submit_id: number;
  exam_id: number;
  student_id: number;
  total_score?: number | null;
  teacher_comment?: string | null;
  answers_json?: Record<string, string> | Array<Record<string, unknown>> | null;
  submit_time: string;
}

export const examApi = {
  /** GET /exams：考试列表 */
  list: (status?: string) => request.get<ExamItem[]>("/exams", { params: status ? { status } : undefined }),

  /** POST /exams：教师/管理员创建考试 */
  create: (payload: ExamCreatePayload) => request.post<ExamItem>("/exams", payload),

  /** GET /exams/{exam_id}：考试详情 */
  detail: (examId: number) => request.get<ExamDetail>(`/exams/${examId}`),

  /** PATCH /exams/{exam_id}：更新考试 */
  update: (examId: number, payload: ExamUpdatePayload) => request.patch<ExamItem>(`/exams/${examId}`, payload),

  /** DELETE /exams/{exam_id}：软删除考试 */
  delete: (examId: number) => request.delete<boolean>(`/exams/${examId}`),

  /** POST /exams/{exam_id}/questions：组卷加题 */
  addQuestion: (examId: number, payload: ExamQuestionPayload) => request.post<ExamQuestionItem>(`/exams/${examId}/questions`, payload),

  /** GET /exams/{exam_id}/questions：试卷题目列表 */
  questions: (examId: number) => request.get<ExamQuestionItem[]>(`/exams/${examId}/questions`),

  /** DELETE /exams/{exam_id}/questions/{question_id}：从试卷移除题目 */
  removeQuestion: (examId: number, questionId: number) => request.delete<boolean>(`/exams/${examId}/questions/${questionId}`),

  /** GET /exams/{exam_id}/start：学生进入考试 */
  start: (examId: number) => request.get<ExamDetail>(`/exams/${examId}/start`),

  /** POST /exams/{exam_id}/submit：学生提交考试答案 */
  submit: (examId: number, answers: Record<string, string> | Array<Record<string, unknown>>) =>
    request.post<ExamSubmissionItem>(`/exams/${examId}/submit`, { answers }),

  /** GET /exams/submissions/me：我的考试记录 */
  mySubmissions: () => request.get<ExamSubmissionItem[]>("/exams/submissions/me"),

  /** GET /exams/{exam_id}/submissions：某考试提交记录 */
  submissions: (examId: number) => request.get<ExamSubmissionItem[]>(`/exams/${examId}/submissions`),

  /** PUT /exams/submissions/{exam_submit_id}/review：教师复核成绩 */
  review: (submitId: number, payload: { total_score: number; teacher_comment?: string | null }) =>
    request.put<ExamSubmissionItem>(`/exams/submissions/${submitId}/review`, payload),
};
