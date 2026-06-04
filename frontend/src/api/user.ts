import request from "./request";
import type { User } from "./auth";

export interface UserProfile {
  user: User;
  stats: {
    total_answers: number;
    correct_answers: number;
    accuracy: number;
    knowledge_points_tracked: number;
    mastered_count: number;
  };
  joined_at: string;
}

export const fetchUserProfile = (userId: number): Promise<UserProfile> =>
  request.get(`/user/profile/${userId}`);

export const changePassword = (params: {
  old_password: string;
  new_password: string;
}) => request.post("/user/change-password", params);
