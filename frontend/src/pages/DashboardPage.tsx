import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import DashboardLayout, {
  type DashboardView,
} from "../components/DashboardLayout/DashboardLayout";

import HomeDashboardView from "./HomeDashboardView";
import PracticePage from "./PracticePage";
import { adminApi, type AdminDashboardStats } from "../api/admin";

import "../styles/pages/DashboardPage.css";
import "../styles/pages/CourseManagementView.css";
import "../styles/pages/KnowledgeWarehousePage.css";
import "../styles/pages/ProfileView.css";
import "../styles/pages/ReportView.css";
import "../styles/pages/SettingsView.css";

interface DashboardPageProps {
  userId: number;
  username?: string;
  role: "admin" | "teacher" | "student";
  onLogout: () => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({
  userId,
  username,
  role,
  onLogout,
}) => {
  const navigate = useNavigate();

  const [showPractice, setShowPractice] = useState(false);
  const [practiceKnowledgeId, setPracticeKnowledgeId] = useState<
    number | undefined
  >();
  const [adminStats, setAdminStats] = useState<AdminDashboardStats | null>(null);
  const [adminStatsError, setAdminStatsError] = useState("");

  useEffect(() => {
    if (role !== "admin") {
      return;
    }

    adminApi
      .getDashboardStats()
      .then((data) => {
        setAdminStats(data);
        setAdminStatsError("");
      })
      .catch((error) => {
        setAdminStatsError(error instanceof Error ? error.message : "管理员统计加载失败");
      });
  }, [role]);

  const roleCountMap = useMemo(() => {
    return Object.fromEntries((adminStats?.roles ?? []).map((item) => [item.role, item.count]));
  }, [adminStats]);

  const openPractice = (knowledgeId?: number) => {
    setPracticeKnowledgeId(knowledgeId);
    setShowPractice(true);
  };

  const handleNavigate = (view: DashboardView) => {
    if (view === "home") {
      navigate("/dashboard");
      return;
    }

    if (view === "student-courses" || view === "courses") {
      navigate("/courses");
      return;
    }

    if (view === "warehouse") {
      navigate("/knowledge");
      return;
    }

    if (view === "report") {
      navigate("/report");
      return;
    }

    if (view === "tasks") {
      navigate("/tasks");
      return;
    }

    if (view === "exams") {
      navigate("/exams");
      return;
    }

    if (view === "profile") {
      navigate("/profile");
      return;
    }

    if (view === "settings") {
      navigate("/settings");
      return;
    }
  };

  return (
    <>
      {showPractice && (
        <PracticePage
          userId={userId}
          knowledgeId={practiceKnowledgeId}
          onClose={() => {
            setShowPractice(false);
            setPracticeKnowledgeId(undefined);
          }}
        />
      )}

      <DashboardLayout
        activeView="home"
        onNavigate={handleNavigate}
        onLogout={onLogout}
        role={role}
      >
        {role === "student" && (
          <HomeDashboardView
            userId={userId}
            username={username}
            onPractice={() => openPractice()}
          />
        )}

        {role === "teacher" && (
          <>
            <section className="dashboard-header">
              <div>
                <h1>教学概览</h1>
                <p>欢迎回来，{username || "老师"}，这里是你的教学工作台。</p>
              </div>
            </section>

            <div className="dashboard-grid">
              <section className="study-card">
                <h2>教学概况</h2>

                <div className="study-summary">
                  <div>
                    <strong>0</strong>
                    <span>已开课程</span>
                  </div>
                  <div>
                    <strong>0</strong>
                    <span>负责教学班</span>
                  </div>
                  <div>
                    <strong>0</strong>
                    <span>学生总数</span>
                  </div>
                </div>
              </section>

              <section className="course-card">
                <h2>我的课程</h2>
                <p className="course-empty">后续这里接入老师负责的课程数据。</p>
              </section>

              <section className="course-card">
                <h2>我的教学班</h2>
                <p className="course-empty">
                  后续这里接入老师负责的教学班数据。
                </p>
              </section>

              <section className="course-card">
                <h2>课程管理快捷入口</h2>

                <div className="course-header-actions">
                  <button
                    className="course-btn primary"
                    type="button"
                    onClick={() => navigate("/courses")}
                  >
                    新开课程
                  </button>

                  <button
                    className="course-btn ghost"
                    type="button"
                    onClick={() => navigate("/courses")}
                  >
                    课程管理
                  </button>
                </div>
              </section>

              <section className="course-card">
                <h2>教学班管理快捷入口</h2>

                <div className="course-header-actions">
                  <button className="course-btn primary" type="button">
                    新开教学班
                  </button>

                  <button className="course-btn ghost" type="button">
                    导出学生名单
                  </button>
                </div>
              </section>
            </div>
          </>
        )}

        {role === "admin" && (
          <>
            <section className="dashboard-header">
              <div>
                <h1>管理概览</h1>
                <p>
                  欢迎回来，{username || "管理员"}，这里是系统管理工作台。
                </p>
              </div>
            </section>

            <div className="dashboard-grid">
              <section className="study-card">
                <h2>用户统计</h2>

                <div className="study-summary">
                  <div>
                    <strong>{roleCountMap.student ?? 0}</strong>
                    <span>学生数量</span>
                  </div>
                  <div>
                    <strong>{roleCountMap.teacher ?? 0}</strong>
                    <span>教师数量</span>
                  </div>
                  <div>
                    <strong>{roleCountMap.admin ?? 0}</strong>
                    <span>管理员数量</span>
                  </div>
                </div>
              </section>

              <section className="course-card">
                <h2>用户管理</h2>
                <p className="course-empty">
                  可以修改用户角色、删除用户、修改用户信息、导出某一角色的所有用户信息。
                </p>

                <div className="course-header-actions">
                  <button
                    className="course-btn primary"
                    type="button"
                    onClick={() => navigate("/users")}
                  >
                    进入用户管理
                  </button>
                </div>
              </section>

              <section className="course-card">
                <h2>课程管理</h2>
                <p className="course-empty">
                  管理员可以查看和维护平台课程信息。
                </p>

                <div className="course-header-actions">
                  <button
                    className="course-btn ghost"
                    type="button"
                    onClick={() => navigate("/courses")}
                  >
                    进入课程管理
                  </button>
                </div>
              </section>
            </div>
          </>
        )}
      </DashboardLayout>
    </>
  );
};

export default DashboardPage;