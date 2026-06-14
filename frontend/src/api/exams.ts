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
}

export interface ExamQuestionItem {
  exam_question_id: number;
  exam_id: number;
  question_id: number;
  score: number;
  sort_order: number;
  stem?: string;
  question_type?: string;
  option_a?: string | null;
  option_b?: string | null;
  option_c?: string | null;
  option_d?: string | null;
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
  answers_json?: Record<string, string> | null;
  submit_time: string;
}

export const examApi = {
  list: () => request.get<ExamItem[]>("/v1/exams"),
  create: (payload: { title: string; course_id: number; duration_minutes: number; exam_type: string; status: string }) =>
    request.post<ExamItem>("/v1/exams", payload),
  detail: (examId: number) => request.get<ExamDetail>(`/v1/exams/${examId}`),
  delete: (examId: number) => request.delete(`/v1/exams/${examId}`),
  addQuestion: (examId: number, payload: { question_id: number; score: number; sort_order: number }) =>
    request.post<ExamQuestionItem>(`/v1/exams/${examId}/questions`, payload),
  start: (examId: number) => request.get<ExamDetail>(`/v1/exams/${examId}/start`),
  submit: (examId: number, answers: Record<string, string>) =>
    request.post<ExamSubmissionItem>(`/v1/exams/${examId}/submit`, { answers }),
  mySubmissions: () => request.get<ExamSubmissionItem[]>("/v1/exams/submissions/me"),
  submissions: (examId: number) => request.get<ExamSubmissionItem[]>(`/v1/exams/${examId}/submissions`),
  review: (submitId: number, payload: { total_score?: number; teacher_comment?: string }) =>
    request.put<ExamSubmissionItem>(`/v1/exams/submissions/${submitId}/review`, payload),
};
