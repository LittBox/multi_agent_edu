import request from "./request";

export interface Question {
  question_id: number | null;
  knowledge_id: number | null;
  question_type?: string;
  stem?: string;
  option_a?: string | null;
  option_b?: string | null;
  option_c?: string | null;
  option_d?: string | null;
  answer?: string;
  difficulty?: number;
  image_url?: string | null;
  explanation?: string | null;
  reason?: string;
  message?: string;
  requested_knowledge_id?: number | null;
}

export interface QuestionCreateParams {
  knowledge_id?: number | null;
  question_type: string;
  stem: string;
  answer: string;
  option_a?: string | null;
  option_b?: string | null;
  option_c?: string | null;
  option_d?: string | null;
  explanation?: string | null;
  difficulty?: number;
  image_url?: string | null;
}

export type QuestionUpdateParams = Partial<QuestionCreateParams>;

export interface SubmitAnswerParams {
  user_id: number;
  question_id: number;
  user_answer: string;
  quality_q?: number;
  time_spent_seconds?: number;
}

export interface SubmitAnswerEvent {
  id?: string;
  type: string;
  source: string;
  timestamp: string;
  learner_id?: string;
  data: Record<string, unknown>;
}

export interface SubmitAnswerResult {
  is_correct: boolean;
  correct_answer: string;
  explanation: string | null;
  knowledge_id: number;
  question_id?: number;
  events_triggered: number;
  agent_reply?: string | null;
  events: SubmitAnswerEvent[];
}

export interface LearnerProgress {
  knowledge_id: number;
  name: string;
  subject: string;
  mastery: number;
  mastery_percent: number;
  confidence: number;
  attempts: number;
  correct_attempts: number;
  streak: number;
  status: "mastered" | "learning";
  last_practiced_at: string | null;
}

export interface ReviewItem {
  knowledge_id: number;
  name: string;
  subject: string;
  next_review_at: string;
  last_review_at: string | null;
  interval_days: number;
  repetition: number;
  ef: number;
  is_due: boolean;
}

export interface AnswerHistory {
  total: number;
  items: Array<{
    record_id: number;
    question_id: number;
    knowledge_id: number;
    knowledge_name: string;
    stem: string;
    user_answer: string | null;
    is_correct: boolean;
    submitted_at: string;
    time_spent_seconds: number | null;
  }>;
}

export interface LearningReportOverview {
  total_answers: number;
  correct_answers: number;
  accuracy: number;
  mastered_count: number;
  learning_count: number;
  knowledge_points_tracked: number;
  today_study_minutes: number;
}

export interface LearningProfileDimension {
  key: string;
  label: string;
  score: number;
  raw: Record<string, number | string | boolean | null>;
  source: string;
  formula: string;
}

export interface LearningProfile {
  window_days: number;
  target_answers: number;
  radar: LearningProfileDimension[];
}

export interface LearningReport {
  overview: LearningReportOverview;
  summary?: LearningReportOverview;
  profile: LearningProfile;
  weak_points: Array<{
    knowledge_id: number;
    name: string;
    subject: string;
    mastery: number;
    mastery_percent: number;
    attempts: number;
  }>;
  subject_stats: Array<{
    subject: string;
    count: number;
    avg_mastery: number;
  }>;
  daily_accuracy: Array<{
    date: string;
    total: number;
    correct: number;
    accuracy: number;
  }>;
  recent_answers: Array<{
    record_id: number;
    question_id: number;
    knowledge_id: number;
    is_correct: boolean;
    submitted_at: string | null;
  }>;
}

/** 题库列表：GET /education/questions */
export const fetchQuestions = (
  userId: number,
  knowledgeId?: number
): Promise<Question[]> =>
  request.get("/education/questions", {
    params: {
      user_id: userId,
      ...(knowledgeId ? { knowledge_id: knowledgeId } : {}),
    },
  });

export const createQuestion = (
  params: QuestionCreateParams
): Promise<Question> => request.post("/education/questions", params);

export const getQuestion = (questionId: number): Promise<Question> =>
  request.get(`/education/questions/${questionId}`);

export const updateQuestion = (
  questionId: number,
  params: QuestionUpdateParams
): Promise<Question> =>
  request.patch(`/education/questions/${questionId}`, params);

export const deleteQuestion = (questionId: number): Promise<boolean> =>
  request.delete(`/education/questions/${questionId}`);

export const fetchNextQuestion = (
  userId: number,
  knowledgeId?: number
): Promise<Question | null> =>
  request.get(`/education/next-question/${userId}`, {
    params: knowledgeId ? { knowledge_id: knowledgeId } : undefined,
  });

export const submitAnswer = (
  params: SubmitAnswerParams
): Promise<SubmitAnswerResult> => request.post("/education/submit", params);

export const fetchProgress = (
  userId: number
): Promise<LearnerProgress[]> => request.get(`/education/progress/${userId}`);

export const fetchReviews = (
  userId: number,
  dueOnly = true
): Promise<ReviewItem[]> =>
  request.get(`/education/reviews/${userId}`, {
    params: { due_only: dueOnly },
  });

export const fetchAnswerHistory = (
  userId: number,
  limit = 20,
  offset = 0
): Promise<AnswerHistory> =>
  request.get(`/education/answers/${userId}`, {
    params: { limit, offset },
  });

export const fetchLearningReport = (
  userId: number
): Promise<LearningReport> => request.get(`/education/report/${userId}`);

export const tutorAsk = (params: {
  user_id: number;
  knowledge_id: number;
  question: string;
}) => request.post("/education/question", params);

export const tutorMessage = (params: {
  user_id: number;
  message: string;
  knowledge_id?: number;
}) => request.post("/education/message", params);

export const requestHint = (params: {
  user_id: number;
  knowledge_id: number;
  question_id?: number;
}) => request.post("/education/hint", params);

export const explainAnswer = (params: {
  user_id: number;
  knowledge_id: number;
  question?: string;
  user_answer?: string;
  correct_answer?: string;
  is_correct?: boolean | null;
}) => request.post("/education/explain", params);