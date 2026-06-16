import { create } from "zustand";
import {
  fetchDashboard,
  fetchKnowledgeCards,
  type DashboardData,
  type KnowledgeCard,
} from "../api/dashboard";

/** 仪表盘 Store：管理学习首页统计和知识卡片。 */
interface DashboardStore {
  dashboard: DashboardData | null;
  knowledgeCards: KnowledgeCard[];
  loading: boolean;
  error: string | null;

  clearError: () => void;
  loadDashboard: (userId: number) => Promise<DashboardData>;
  loadKnowledgeCards: (userId: number) => Promise<KnowledgeCard[]>;
  loadHomeData: (userId: number) => Promise<{ dashboard: DashboardData; knowledgeCards: KnowledgeCard[] }>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useDashboardStore = create<DashboardStore>((set, get) => ({
  dashboard: null,
  knowledgeCards: [],
  loading: false,
  error: null,

  clearError: () => set({ error: null }),

  loadDashboard: async (userId) => {
    set({ loading: true, error: null });
    try {
      const dashboard = await fetchDashboard(userId);
      set({ dashboard, loading: false });
      return dashboard;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载仪表盘失败") });
      throw error;
    }
  },

  loadKnowledgeCards: async (userId) => {
    const knowledgeCards = await fetchKnowledgeCards(userId);
    set({ knowledgeCards });
    return knowledgeCards;
  },

  loadHomeData: async (userId) => {
    set({ loading: true, error: null });
    try {
      const [dashboard, knowledgeCards] = await Promise.all([
        get().loadDashboard(userId),
        get().loadKnowledgeCards(userId),
      ]);
      set({ loading: false });
      return { dashboard, knowledgeCards };
    } catch (error) {
      set({ loading: false, error: getError(error, "加载首页数据失败") });
      throw error;
    }
  },
}));
