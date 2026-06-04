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

export interface AgentSuggestionBlock {
  title: string;
  detail: string;
  knowledge_name?: string;
}

export interface AgentSuggestions {
  start_learning: AgentSuggestionBlock;
  weak_point: AgentSuggestionBlock;
  encouragement: AgentSuggestionBlock;
}

export const fetchDashboard = (userId: number): Promise<DashboardData> =>
  request.get(`/dashboard/${userId}`);

export const fetchKnowledgeCards = (userId: number): Promise<KnowledgeCard[]> =>
  request.get(`/knowledge-cards/${userId}`);

export const fetchAgentSuggestions = (userId: number): Promise<AgentSuggestions> =>
  request.get(`/agent-suggestions/${userId}`);
