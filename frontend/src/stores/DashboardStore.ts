import { create } from "zustand";
import {
  fetchDashboard,
  type DashboardData,
  type KnowledgeCard,
} from "../api/dashboard";
import {
  fetchProgress,
  type LearnerProgress,
} from "../api/education";

/** 仪表盘 Store：管理学习首页统计和知识卡片。 */
interface DashboardStore {
  dashboard: DashboardData | null;
  knowledgeCards: KnowledgeCard[];
  loading: boolean;
  error: string | null;

  clearError: () => void;
  loadDashboard: (userId: number) => Promise<DashboardData>;
  loadKnowledgeCards: (userId: number) => Promise<KnowledgeCard[]>;
  loadHomeData: (userId: number) => Promise<{
    dashboard: DashboardData;
    knowledgeCards: KnowledgeCard[];
  }>;
}

const getError = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

const toMasteryPercent = (item: { mastery?: number; mastery_percent?: number }) => {
  const explicit = Number(item.mastery_percent);

  if (Number.isFinite(explicit)) {
    return Math.max(0, Math.min(100, Math.round(explicit)));
  }

  return Math.max(0, Math.min(100, Math.round(Number(item.mastery ?? 0) * 100)));
};

const progressToKnowledgeCard = (item: LearnerProgress): KnowledgeCard => ({
  knowledge_id: item.knowledge_id,
  name: item.name,
  mastery: Number(item.mastery ?? 0),
  mastery_percent: toMasteryPercent(item),
  attempts: Number(item.attempts ?? 0),
  streak: Number(item.streak ?? 0),
});

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
    const progress = await fetchProgress(userId);

    const knowledgeCards = progress
      .map(progressToKnowledgeCard)
      .sort((a, b) => {
        if (b.attempts !== a.attempts) return b.attempts - a.attempts;
        return b.mastery_percent - a.mastery_percent;
      });

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