import request from "./request";

export type KnowledgeStatus =
  | "mastered"
  | "learning"
  | "not_started"
  | "locked";

export interface KnowledgeRepositoryItem {
  knowledge_id: number;
  name: string;
  subject: string;
  description: string;
  difficulty: number;
  parent_id: number | null;
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

export const fetchKnowledgeRepository = (
  userId: number,
  params?: { q?: string; subject?: string }
): Promise<KnowledgeRepositoryData> =>
  request.get(`/knowledge/repository/${userId}`, { params });

export const createKnowledgePoint = (params: {
  name: string;
  subject: string;
  description?: string;
  parent_id?: number | null;
  difficulty?: number;
}) => request.post("/knowledge", params);

export const deleteKnowledgePoint = (knowledgeId: number) =>
  request.delete(`/knowledge/${knowledgeId}`);
