import request from "./request";

export type KnowledgeStatus = "mastered" | "learning" | "not_started" | "locked";

export interface KnowledgeRepositoryItem {
  knowledge_id: number;
  name: string;
  subject: string;
  description: string;
  difficulty: number;
  parent_id: number | null;
  created_at: string;
  mastery: number;
  mastery_percent: number;
  attempts: number;
  streak: number;
  status: KnowledgeStatus;
  question_count: number;
}

export interface KnowledgeRepositoryData {
  items: KnowledgeRepositoryItem[];
  subjects: string[];
  total: number;
}

export interface KnowledgePointPayload {
  name: string;
  subject: string;
  description?: string | null;
  parent_id?: number | null;
  difficulty?: number;
}

export interface KnowledgePointSimple {
  knowledge_id: number;
  name: string;
  subject: string;
  description?: string | null;
  difficulty?: number;
  parent_id?: number | null;
  created_at?: string;
}

export interface JoinedKnowledgePointResponse {
  knowledge_id: number;
  name: string;
  subject: string;
  created_at: string;
  joined_at: string;
  mastery: number;
  mastery_percent: number;
  attempts: number;
  streak: number;
}

export const fetchKnowledgeRepository = (
  userId: number,
  params?: { q?: string; subject?: string }
): Promise<KnowledgeRepositoryData> => request.get(`/knowledge/repository/${userId}`, { params });

export const fetchKnowledgeDetail = (knowledgeId: number, userId: number) =>
  request.get(`/knowledge/detail/${knowledgeId}`, { params: { user_id: userId } });

export const createKnowledgePoint = (params: KnowledgePointPayload): Promise<KnowledgePointSimple> =>
  request.post("/knowledge", params);

export const updateKnowledgePoint = (
  knowledgeId: number,
  params: Partial<KnowledgePointPayload>
): Promise<KnowledgePointSimple> => request.patch(`/knowledge/${knowledgeId}`, params);

export const joinKnowledgePoint = (
  knowledgeId: number,
  userId: number
): Promise<JoinedKnowledgePointResponse> =>
  request.post(`/knowledge/${knowledgeId}/join`, null, { params: { user_id: userId } });

export const deleteKnowledgePoint = (knowledgeId: number): Promise<boolean> =>
  request.delete(`/knowledge/${knowledgeId}`);

export const fetchAllPoints = (): Promise<KnowledgePointSimple[]> =>
  request.get("/knowledge/all-points");
