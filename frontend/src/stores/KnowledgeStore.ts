import { create } from "zustand";
import {
  createKnowledgePoint,
  deleteKnowledgePoint,
  fetchAllPoints,
  fetchKnowledgeDetail,
  fetchKnowledgeRepository,
  joinKnowledgePoint,
  updateKnowledgePoint,
  type JoinedKnowledgePointResponse,
  type KnowledgePointPayload,
  type KnowledgePointSimple,
  type KnowledgeRepositoryData,
  type KnowledgeRepositoryItem,
} from "../api/knowledge";

/** 知识仓库 Store：管理知识点列表、仓库筛选条件和加入知识点状态。 */
interface KnowledgeStore {
  repository: KnowledgeRepositoryData | null;
  items: KnowledgeRepositoryItem[];
  subjects: string[];
  allPoints: KnowledgePointSimple[];
  selectedDetail: unknown | null;
  loading: boolean;
  error: string | null;
  query: string;
  subject: string;

  setQuery: (query: string) => void;
  setSubject: (subject: string) => void;
  clearError: () => void;
  loadRepository: (userId: number, params?: { q?: string; subject?: string }) => Promise<KnowledgeRepositoryData>;
  loadDetail: (knowledgeId: number, userId: number) => Promise<unknown>;
  loadAllPoints: () => Promise<KnowledgePointSimple[]>;
  createPoint: (params: KnowledgePointPayload) => Promise<KnowledgePointSimple>;
  updatePoint: (knowledgeId: number, params: Partial<KnowledgePointPayload>) => Promise<KnowledgePointSimple>;
  deletePoint: (knowledgeId: number) => Promise<void>;
  joinPoint: (knowledgeId: number, userId: number) => Promise<JoinedKnowledgePointResponse>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useKnowledgeStore = create<KnowledgeStore>((set, get) => ({
  repository: null,
  items: [],
  subjects: [],
  allPoints: [],
  selectedDetail: null,
  loading: false,
  error: null,
  query: "",
  subject: "全部",

  setQuery: (query) => set({ query }),
  setSubject: (subject) => set({ subject }),
  clearError: () => set({ error: null }),

  loadRepository: async (userId, params) => {
    const q = params?.q ?? get().query;
    const subject = params?.subject ?? (get().subject === "全部" ? undefined : get().subject);
    set({ loading: true, error: null });
    try {
      const repository = await fetchKnowledgeRepository(userId, { q, subject });
      set({
        repository,
        items: repository.items,
        subjects: repository.subjects,
        loading: false,
      });
      return repository;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载知识仓库失败") });
      throw error;
    }
  },

  loadDetail: async (knowledgeId, userId) => {
    const detail = await fetchKnowledgeDetail(knowledgeId, userId);
    set({ selectedDetail: detail });
    return detail;
  },

  loadAllPoints: async () => {
    const allPoints = await fetchAllPoints();
    set({ allPoints });
    return allPoints;
  },

  createPoint: async (params) => {
    const point = await createKnowledgePoint(params);
    set((state) => ({ allPoints: [point, ...state.allPoints] }));
    return point;
  },

  updatePoint: async (knowledgeId, params) => {
    const updated = await updateKnowledgePoint(knowledgeId, params);
    set((state) => ({
      allPoints: state.allPoints.map((item) => item.knowledge_id === knowledgeId ? updated : item),
      items: state.items.map((item) => item.knowledge_id === knowledgeId ? { ...item, ...updated, description: updated.description ?? "",} : item),
    }));
    return updated;
  },

  deletePoint: async (knowledgeId) => {
    await deleteKnowledgePoint(knowledgeId);
    set((state) => ({
      allPoints: state.allPoints.filter((item) => item.knowledge_id !== knowledgeId),
      items: state.items.filter((item) => item.knowledge_id !== knowledgeId),
    }));
  },

  joinPoint: async (knowledgeId, userId) => {
    const joined = await joinKnowledgePoint(knowledgeId, userId);

    await get().loadRepository(userId);

    return joined;
  },
}));
