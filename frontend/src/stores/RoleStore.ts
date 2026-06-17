import { create } from "zustand";
import {
  roleApi,
  type StudentRoleUser,
  type StudentInfoUpdatePayload,
} from "../api/role";

interface RoleStore {
  studentInfo: StudentRoleUser | null;
  loading: boolean;
  error: string | null;

  getMyStudentInfo: () => Promise<StudentRoleUser>;
  updateMyStudentInfo: (payload: StudentInfoUpdatePayload) => Promise<StudentRoleUser>;
}

export const useRoleStore = create<RoleStore>((set) => ({
  studentInfo: null,
  loading: false,
  error: null,

  getMyStudentInfo: async () => {
    set({ loading: true, error: null });

    try {
      const studentInfo = await roleApi.getMyStudentInfo();

      set({
        studentInfo,
        loading: false,
      });

      return studentInfo;
    } catch (error) {
      set({
        loading: false,
        error: "加载学生信息失败",
      });

      throw error;
    }
  },

  updateMyStudentInfo: async (payload) => {
    set({ loading: true, error: null });

    try {
      const updated = await roleApi.updateMyStudentInfo(payload);

      set({
        studentInfo: updated,
        loading: false,
      });

      return updated;
    } catch (error) {
      set({
        loading: false,
        error: "更新学生信息失败",
      });

      throw error;
    }
  },
}));