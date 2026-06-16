import { create } from "zustand";
import {
  changePassword,
  fetchUserProfile,
  updateUserProfile,
  type UserProfile,
  type UserProfileUpdateParams,
} from "../api/user";
import type { ChangePasswordParams } from "../api/auth";

/** 用户中心 Store：管理个人主页、资料更新和密码修改。 */
interface UserStore {
  profile: UserProfile | null;
  loading: boolean;
  error: string | null;
  message: string | null;

  clearError: () => void;
  clearMessage: () => void;
  loadProfile: (userId: number) => Promise<UserProfile>;
  updateProfile: (userId: number, params: UserProfileUpdateParams) => Promise<UserProfile>;
  changePassword: (params: ChangePasswordParams) => Promise<boolean>;
}

const getError = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export const useUserStore = create<UserStore>((set) => ({
  profile: null,
  loading: false,
  error: null,
  message: null,

  clearError: () => set({ error: null }),
  clearMessage: () => set({ message: null }),

  loadProfile: async (userId) => {
    set({ loading: true, error: null });
    try {
      const profile = await fetchUserProfile(userId);
      set({ profile, loading: false });
      return profile;
    } catch (error) {
      set({ loading: false, error: getError(error, "加载用户主页失败") });
      throw error;
    }
  },

  updateProfile: async (userId, params) => {
    const profile = await updateUserProfile(userId, params);
    set({ profile, message: "资料更新成功" });
    return profile;
  },

  changePassword: async (params) => {
    const result = await changePassword(params);
    set({ message: "密码修改成功" });
    return result;
  },
}));
