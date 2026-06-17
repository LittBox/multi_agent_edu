import { create } from "zustand";
import {
  createQuestion,
  deleteQuestion,
  explainAnswer,
  fetchAnswerHistory,
  fetchLearningReport,
  fetchNextQuestion,
  fetchProgress,
  fetchQuestions,
  fetchReviews,
  getQuestion,
  requestHint,
  submitAnswer,
  tutorAsk,
  tutorMessage,
  updateQuestion,
  type AnswerHistory,
  type LearnerProgress,
  type LearningReport,
  type Question,
  type QuestionCreateParams,
  type QuestionUpdateParams,
  type ReviewItem,
  type SubmitAnswerParams,
  type SubmitAnswerResult,
} from "../api/education";
import { useDashboardStore } from "./DashboardStore";
import { useKnowledgeStore } from "./KnowledgeStore";
/** 学习练习与题库 Store：管理练习题、提交答案、学习进度、复习计划和学习报告。 */
interface EducationStore {
  questions: Question[];
  currentQuestion: Question | null;
  answerResult: SubmitAnswerResult | null;
  progress: LearnerProgress[];
  reviews: ReviewItem[];
  answerHistory: AnswerHistory | null;
  report: LearningReport | null;
  tutorResult: unknown | null;
  loading: boolean;
  error: string | null;

  clearError: () => void;
  loadQuestions: (userId: number, knowledgeId?: number) => Promise<Question[]>;
  loadQuestion: (questionId: number) => Promise<Question>;
  createQuestion: (params: QuestionCreateParams) => Promise<Question>;
  updateQuestion: (questionId: number, params: QuestionUpdateParams) => Promise<Question>;
  deleteQuestion: (questionId: number) => Promise<void>;
  loadNextQuestion: (userId: number, knowledgeId?: number) => Promise<Question | null>;
  submitAnswer: (params: SubmitAnswerParams) => Promise<SubmitAnswerResult>;
  loadProgress: (userId: number) => Promise<LearnerProgress[]>;
  loadReviews: (userId: number, dueOnly?: boolean) => Promise<ReviewItem[]>;
  loadAnswerHistory: (userId: number, limit?: number, offset?: number) => Promise<AnswerHistory>;
  loadReport: (userId: number) => Promise<LearningReport>;
  askTutor: (params: { user_id: number; knowledge_id: number; question: string }) => Promise<unknown>;
  sendTutorMessage: (params: { user_id: number; message: string; knowledge_id?: number }) => Promise<unknown>;
  getHint: (params: { user_id: number; knowledge_id: number; question_id?: number }) => Promise<unknown>;
  getExplanation: (params: Parameters<typeof explainAnswer>[0]) => Promise<unknown>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useEducationStore = create<EducationStore>((set, get) => ({
  questions: [],
  currentQuestion: null,
  answerResult: null,
  progress: [],
  reviews: [],
  answerHistory: null,
  report: null,
  tutorResult: null,
  loading: false,
  error: null,

  clearError: () => set({ error: null }),

  loadQuestions: async (userId, knowledgeId) => {
    set({ loading: true, error: null });
    try {
      const questions = await fetchQuestions(userId, knowledgeId);
      set({ questions, loading: false });
      return questions;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载题目失败") });
      throw error;
    }
  },

  loadQuestion: async (questionId) => {
    const question = await getQuestion(questionId);
    set({ currentQuestion: question });
    return question;
  },

  createQuestion: async (params) => {
    const question = await createQuestion(params);
    set((state) => ({ questions: [question, ...state.questions] }));
    return question;
  },

  updateQuestion: async (questionId, params) => {
    const updated = await updateQuestion(questionId, params);
    set((state) => ({
      questions: state.questions.map((item) => item.question_id === questionId ? updated : item),
      currentQuestion: state.currentQuestion?.question_id === questionId ? updated : state.currentQuestion,
    }));
    return updated;
  },

  deleteQuestion: async (questionId) => {
    await deleteQuestion(questionId);
    set((state) => ({ questions: state.questions.filter((item) => item.question_id !== questionId) }));
  },

  loadNextQuestion: async (userId, knowledgeId) => {
    const question = await fetchNextQuestion(userId, knowledgeId);
    set({ currentQuestion: question });
    return question;
  },

  submitAnswer: async (params) => {
    const result = await submitAnswer(params);
    set({ answerResult: result });

    await Promise.allSettled([
      get().loadProgress(params.user_id),
      get().loadReviews(params.user_id, false),
      useKnowledgeStore.getState().loadRepository(params.user_id),
      useDashboardStore.getState().loadHomeData(params.user_id),
    ]);

    return result;
  },

  loadProgress: async (userId) => {
    const progress = await fetchProgress(userId);
    set({ progress });
    return progress;
  },

  loadReviews: async (userId, dueOnly = true) => {
    const reviews = await fetchReviews(userId, dueOnly);
    set({ reviews });
    return reviews;
  },

  loadAnswerHistory: async (userId, limit = 20, offset = 0) => {
    const answerHistory = await fetchAnswerHistory(userId, limit, offset);
    set({ answerHistory });
    return answerHistory;
  },

  loadReport: async (userId) => {
    const report = await fetchLearningReport(userId);
    set({ report });
    return report;
  },

  askTutor: async (params) => {
    const result = await tutorAsk(params);
    set({ tutorResult: result });
    return result;
  },

  sendTutorMessage: async (params) => {
    const result = await tutorMessage(params);
    set({ tutorResult: result });
    return result;
  },

  getHint: async (params) => {
    const result = await requestHint(params);
    set({ tutorResult: result });
    return result;
  },

  getExplanation: async (params) => {
    const result = await explainAnswer(params);
    set({ tutorResult: result });
    return result;
  },
}));
