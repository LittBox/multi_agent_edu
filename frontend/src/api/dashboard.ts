import request from "./request";

export interface StudyTrendPoint {
  date: string;
  minutes: number;
}

export interface DashboardSummary {
  today_study_minutes: number;
  week_avg_minutes: number;
  streak_days: number;
  trend: StudyTrendPoint[];
}

export interface PathNode {
  knowledge_id: number;
  name: string;
  status: "done" | "learning" | "locked";
  mastery: number;
}

export interface DashboardData {
  summary: DashboardSummary;
  learning_path: PathNode[];
}

export interface KnowledgeCard {
  knowledge_id: number;
  name: string;
  mastery: number;
  mastery_percent: number;
  attempts: number;
  streak: number;
}

export const fetchDashboard = (userId: number): Promise<DashboardData> =>
  request.get(`/dashboard/${userId}`);

export const fetchKnowledgeCards = (userId: number): Promise<KnowledgeCard[]> =>
  request.get(`/knowledge-cards/${userId}`);
