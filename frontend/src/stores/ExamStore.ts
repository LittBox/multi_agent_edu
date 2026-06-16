import { create } from "zustand";
import {
  examApi,
  type ExamCreatePayload,
  type ExamDetail,
  type ExamItem,
  type ExamQuestionItem,
  type ExamQuestionPayload,
  type ExamSubmissionItem,
  type ExamUpdatePayload,
} from "../api/exams";

/** 考试 Store：管理考试列表、考试详情、组卷、进入考试、提交考试和批阅记录。 */
interface ExamStore {
  exams: ExamItem[];
  currentExam: ExamDetail | null;
  questions: ExamQuestionItem[];
  mySubmissions: ExamSubmissionItem[];
  submissions: ExamSubmissionItem[];
  answers: Record<string, string>;
  loading: boolean;
  error: string | null;
  message: string | null;

  clearError: () => void;
  clearMessage: () => void;
  setAnswer: (questionId: number | string, answer: string) => void;
  resetAnswers: () => void;
  loadExams: (status?: string) => Promise<ExamItem[]>;
  createExam: (payload: ExamCreatePayload) => Promise<ExamItem>;
  updateExam: (examId: number, payload: ExamUpdatePayload) => Promise<ExamItem>;
  deleteExam: (examId: number) => Promise<void>;
  loadExamDetail: (examId: number) => Promise<ExamDetail>;
  addQuestion: (examId: number, payload: ExamQuestionPayload) => Promise<ExamQuestionItem>;
  loadQuestions: (examId: number) => Promise<ExamQuestionItem[]>;
  removeQuestion: (examId: number, questionId: number) => Promise<void>;
  startExam: (examId: number) => Promise<ExamDetail>;
  submitExam: (examId: number, answers?: Record<string, string>) => Promise<ExamSubmissionItem>;
  loadMySubmissions: () => Promise<ExamSubmissionItem[]>;
  loadSubmissions: (examId: number) => Promise<ExamSubmissionItem[]>;
  reviewSubmission: (submitId: number, payload: { total_score: number; teacher_comment?: string | null }) => Promise<ExamSubmissionItem>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useExamStore = create<ExamStore>((set, get) => ({
  exams: [],
  currentExam: null,
  questions: [],
  mySubmissions: [],
  submissions: [],
  answers: {},
  loading: false,
  error: null,
  message: null,

  clearError: () => set({ error: null }),
  clearMessage: () => set({ message: null }),
  setAnswer: (questionId, answer) => set((state) => ({ answers: { ...state.answers, [String(questionId)]: answer } })),
  resetAnswers: () => set({ answers: {} }),

  loadExams: async (status) => {
    set({ loading: true, error: null });
    try {
      const exams = await examApi.list(status);
      set({ exams, loading: false });
      return exams;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载考试列表失败") });
      throw error;
    }
  },

  createExam: async (payload) => {
    const exam = await examApi.create(payload);
    set((state) => ({ exams: [exam, ...state.exams], message: "考试创建成功" }));
    return exam;
  },

  updateExam: async (examId, payload) => {
    const updated = await examApi.update(examId, payload);
    set((state) => ({
      exams: state.exams.map((item) => item.exam_id === examId ? updated : item),
      currentExam: state.currentExam?.exam_id === examId ? { ...state.currentExam, ...updated } : state.currentExam,
    }));
    return updated;
  },

  deleteExam: async (examId) => {
    await examApi.delete(examId);
    set((state) => ({ exams: state.exams.filter((item) => item.exam_id !== examId) }));
  },

  loadExamDetail: async (examId) => {
    const currentExam = await examApi.detail(examId);
    set({ currentExam, questions: currentExam.questions ?? [] });
    return currentExam;
  },

  addQuestion: async (examId, payload) => {
    const question = await examApi.addQuestion(examId, payload);
    set((state) => ({ questions: [...state.questions, question] }));
    return question;
  },

  loadQuestions: async (examId) => {
    const questions = await examApi.questions(examId);
    set({ questions });
    return questions;
  },

  removeQuestion: async (examId, questionId) => {
    await examApi.removeQuestion(examId, questionId);
    set((state) => ({ questions: state.questions.filter((item) => item.question_id !== questionId) }));
  },

  startExam: async (examId) => {
    const currentExam = await examApi.start(examId);
    set({ currentExam, questions: currentExam.questions ?? [], answers: {}, message: null });
    return currentExam;
  },

  submitExam: async (examId, answers) => {
    const submission = await examApi.submit(examId, answers ?? get().answers);
    set((state) => ({
      mySubmissions: [submission, ...state.mySubmissions.filter((item) => item.exam_submit_id !== submission.exam_submit_id)],
      currentExam: null,
      answers: {},
      message: `提交成功，得分：${submission.total_score ?? 0}`,
    }));
    return submission;
  },

  loadMySubmissions: async () => {
    const mySubmissions = await examApi.mySubmissions();
    set({ mySubmissions });
    return mySubmissions;
  },

  loadSubmissions: async (examId) => {
    const submissions = await examApi.submissions(examId);
    set({ submissions });
    return submissions;
  },

  reviewSubmission: async (submitId, payload) => {
    const updated = await examApi.review(submitId, payload);
    set((state) => ({
      submissions: state.submissions.map((item) => item.exam_submit_id === submitId ? updated : item),
      mySubmissions: state.mySubmissions.map((item) => item.exam_submit_id === submitId ? updated : item),
    }));
    return updated;
  },
}));
