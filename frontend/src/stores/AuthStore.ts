import { create } from "zustand";
import {
  login as apiLogin,
  logout as apiLogout,
  fetchCurrentUser,
  type User,
} from "../api/auth";

type AuthPageState = "carousel" | "login" | "home";

interface AuthStore {
  page: AuthPageState;
  user: User | null;
  loading: boolean;

  goLogin: () => void;
  initAuth: () => Promise<void>;
  login: (username: string, pwd: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  page: "carousel",
  user: null,
  loading: true,

  goLogin: () => set({ page: "login" }),

  initAuth: async () => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      set({ user: null, page: "carousel", loading: false });
      return;
    }

    try {
      const user = await fetchCurrentUser();
      set({ user, page: "home", loading: false });
    } catch {
      localStorage.removeItem("accessToken");
      set({ user: null, page: "carousel", loading: false });
    }
  },

  login: async (username, pwd) => {
    const { token, user } = await apiLogin({ username, pwd });

    localStorage.setItem("accessToken", token);

    set({
      user,
      page: "home",
    });
  },

  logout: async () => {
    try {
      await apiLogout();
    } finally {
      localStorage.removeItem("accessToken");
      set({
        user: null,
        page: "carousel",
      });
    }
  },
}));