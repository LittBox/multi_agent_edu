import { useEffect } from "react";
import AuthCarousel from "../components/AuthCarousel/AuthCarousel";
import LoginFormPage from "./LoginFormPage";
import DashboardPage from "./DashboardPage";
import { useAuthStore } from "../stores/AuthStore";

export default function AuthPage() {
  const page = useAuthStore((state) => state.page);
  const user = useAuthStore((state) => state.user);
  const loading = useAuthStore((state) => state.loading);
  const initAuth = useAuthStore((state) => state.initAuth);
  const goLogin = useAuthStore((state) => state.goLogin);

  useEffect(() => {
    void initAuth();
  }, [initAuth]);

  if (loading) {
    return (
      <div className="app-loading">
        正在加载系统...
      </div>
    );
  }

  if (user || page === "home") {
    return <DashboardPage />;
  }

  if (page === "login") {
    return <LoginFormPage />;
  }

  return (
    <div className="auth-page">
      <AuthCarousel />

      <div className="auth-entry-panel">
        <h1>智能学习系统</h1>
        <p>请选择身份并登录，进入课程、知识点、作业与考试中心。</p>
        <button type="button" onClick={goLogin}>
          进入登录
        </button>
      </div>
    </div>
  );
}