import { create } from "zustand";
import {
  taskApi,
  type TaskBankCreatePayload,
  type TaskBankItem,
  type TaskBankUpdatePayload,
  type TaskReleaseItem,
  type TaskReleasePayload,
  type TaskReleaseUpdatePayload,
  type TaskSubmissionItem,
} from "../api/tasks";

/** 作业 Store：管理作业题库、作业发布、学生提交和教师批改。 */
interface TaskStore {
  bank: TaskBankItem[];
  releases: TaskReleaseItem[];
  mySubmissions: TaskSubmissionItem[];
  submissions: TaskSubmissionItem[];
  answers: Record<number, string>;
  loading: boolean;
  error: string | null;
  message: string | null;

  clearError: () => void;
  clearMessage: () => void;
  setAnswer: (taskPublishId: number, answer: string) => void;
  loadBank: (params?: { course_id?: number; teacher_id?: number }) => Promise<TaskBankItem[]>;
  createBank: (payload: TaskBankCreatePayload) => Promise<TaskBankItem>;
  updateBank: (taskId: number, payload: TaskBankUpdatePayload) => Promise<TaskBankItem>;
  deleteBank: (taskId: number) => Promise<void>;
  releaseTask: (payload: TaskReleasePayload) => Promise<TaskReleaseItem>;
  loadReleases: () => Promise<TaskReleaseItem[]>;
  updateRelease: (taskPublishId: number, payload: TaskReleaseUpdatePayload) => Promise<TaskReleaseItem>;
  deleteRelease: (taskPublishId: number) => Promise<void>;
  submitTask: (taskPublishId: number, answerContent?: string) => Promise<TaskSubmissionItem>;
  loadMySubmissions: () => Promise<TaskSubmissionItem[]>;
  loadSubmissions: (taskPublishId: number) => Promise<TaskSubmissionItem[]>;
  gradeSubmission: (submitId: number, payload: { score: number; comment?: string | null }) => Promise<TaskSubmissionItem>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useTaskStore = create<TaskStore>((set, get) => ({
  bank: [],
  releases: [],
  mySubmissions: [],
  submissions: [],
  answers: {},
  loading: false,
  error: null,
  message: null,

  clearError: () => set({ error: null }),
  clearMessage: () => set({ message: null }),
  setAnswer: (taskPublishId, answer) => set((state) => ({ answers: { ...state.answers, [taskPublishId]: answer } })),

  loadBank: async (params) => {
    set({ loading: true, error: null });
    try {
      const bank = await taskApi.listBank(params);
      set({ bank, loading: false });
      return bank;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载作业题库失败") });
      throw error;
    }
  },

  createBank: async (payload) => {
    const item = await taskApi.createBank(payload);
    set((state) => ({ bank: [item, ...state.bank], message: "作业创建成功" }));
    return item;
  },

  updateBank: async (taskId, payload) => {
    const updated = await taskApi.updateBank(taskId, payload);
    set((state) => ({ bank: state.bank.map((item) => item.task_id === taskId ? updated : item) }));
    return updated;
  },

  deleteBank: async (taskId) => {
    await taskApi.deleteBank(taskId);
    set((state) => ({ bank: state.bank.filter((item) => item.task_id !== taskId) }));
  },

  releaseTask: async (payload) => {
    const release = await taskApi.release(payload);
    set((state) => ({ releases: [release, ...state.releases], message: "作业发布成功" }));
    return release;
  },

  loadReleases: async () => {
    set({ loading: true, error: null });
    try {
      const releases = await taskApi.listReleases();
      set({ releases, loading: false });
      return releases;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载已发布作业失败") });
      throw error;
    }
  },

  updateRelease: async (taskPublishId, payload) => {
    const updated = await taskApi.updateRelease(taskPublishId, payload);
    set((state) => ({ releases: state.releases.map((item) => item.task_publish_id === taskPublishId ? updated : item) }));
    return updated;
  },

  deleteRelease: async (taskPublishId) => {
    await taskApi.deleteRelease(taskPublishId);
    set((state) => ({ releases: state.releases.filter((item) => item.task_publish_id !== taskPublishId) }));
  },

  submitTask: async (taskPublishId, answerContent) => {
    const answer = answerContent ?? get().answers[taskPublishId]?.trim();
    if (!answer) {
      throw new Error("请输入作业答案");
    }
    const submission = await taskApi.submit(taskPublishId, answer);
    set((state) => ({
      mySubmissions: [submission, ...state.mySubmissions.filter((item) => item.submit_id !== submission.submit_id)],
      answers: { ...state.answers, [taskPublishId]: "" },
      message: "作业提交成功",
    }));
    return submission;
  },

  loadMySubmissions: async () => {
    const mySubmissions = await taskApi.mySubmissions();
    set({ mySubmissions });
    return mySubmissions;
  },

  loadSubmissions: async (taskPublishId) => {
    const submissions = await taskApi.submissions(taskPublishId);
    set({ submissions });
    return submissions;
  },

  gradeSubmission: async (submitId, payload) => {
    const updated = await taskApi.grade(submitId, payload);
    set((state) => ({
      submissions: state.submissions.map((item) => item.submit_id === submitId ? updated : item),
      mySubmissions: state.mySubmissions.map((item) => item.submit_id === submitId ? updated : item),
    }));
    return updated;
  },
}));
