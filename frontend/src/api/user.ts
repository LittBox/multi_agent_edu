import request from "./request";
import type { User, ChangePasswordParams } from "./auth";

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

export interface UserProfileUpdateParams {
  username?: string;
  email?: string | null;
  avatar?: string | null;
}

/** GET /user/profile/{user_id}：用户主页 */
export const fetchUserProfile = (userId: number): Promise<UserProfile> =>
  request.get(`/user/profile/${userId}`);

/** PATCH /user/profile/{user_id}：更新用户主页资料 */
export const updateUserProfile = (
  userId: number,
  params: UserProfileUpdateParams
): Promise<UserProfile> => request.patch(`/user/profile/${userId}`, params);

/** POST /user/change-password：修改当前用户密码 */
export const changePassword = (params: ChangePasswordParams): Promise<boolean> =>
  request.post("/user/change-password", params);
