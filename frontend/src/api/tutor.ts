import request from "./request";

export interface AnswerAnalysisRequest {
  learner_id: string;
  knowledge_id: string;
  question: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean | null;
}

export interface AnswerAnalysisResponse {
  learner_id: string;
  knowledge_id: string;
  is_correct: boolean | null;
  agent: string;
  model: string;
  analysis: string;
}

export function generateAnswerAnalysis(
  payload: AnswerAnalysisRequest
): Promise<AnswerAnalysisResponse> {
  return request.post<AnswerAnalysisResponse>("/tutor/answer-analysis", payload);
}