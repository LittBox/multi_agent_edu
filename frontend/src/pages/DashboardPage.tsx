import { useEffect, useMemo, useState } from "react";
import { BookOpen, CalendarDays, ClipboardList, FileText, GraduationCap, Home, LogOut, Settings, UserRound } from "lucide-react";
import { useAuthStore, useDashboardStore } from "../stores";
import KnowledgeWarehouseView from "./KnowledgeWarehouseView";
import CourseManagementView from "./CourseManagementView";
import StudentCourseView from "./StudentCourseView";
import ExamView from "./ExamView";
import TaskView from "./TaskView";
import ProfileView from "./ProfileView";
import ReportView from "./ReportView";
import SettingsView from "./SettingsView";
import AdminView from "./AdminView";
import "../styles/pages/DashboardPage.css";

type PageKey = "home" | "knowledge" | "courses" | "exams" | "tasks" | "profile" | "report" | "settings" | "admin";

const pageTitle: Record<PageKey, string> = {
  home: "学习首页",
  knowledge: "知识仓库",
  courses: "课程选课",
  exams: "考试中心",
  tasks: "作业中心",
  profile: "个人主页",
  report: "学习报告",
  settings: "系统设置",
  admin: "后台管理",
};

/** 主页面壳：统一侧边导航、角色路由和业务视图切换。 */
export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { dashboard, knowledgeCards, loading, error, loadHomeData } = useDashboardStore();
  const [active, setActive] = useState<PageKey>("home");

  const userId = user?.user_id ?? user?.id ?? 0;
  const role = user?.role ?? "student";

  useEffect(() => {
    if (userId) {
      void loadHomeData(userId);
    }
  }, [userId, loadHomeData]);

  const navItems = useMemo(() => {
    const base = [
      { key: "home" as PageKey, label: "首页", icon: Home },
      { key: "knowledge" as PageKey, label: "知识", icon: BookOpen },
      { key: "courses" as PageKey, label: role === "student" ? "选课" : "课程", icon: GraduationCap },
      { key: "exams" as PageKey, label: "考试", icon: FileText },
      { key: "tasks" as PageKey, label: "作业", icon: ClipboardList },
      { key: "report" as PageKey, label: "报告", icon: CalendarDays },
      { key: "profile" as PageKey, label: "我的", icon: UserRound },
      { key: "settings" as PageKey, label: "设置", icon: Settings },
    ];
    return role === "admin" ? [...base, { key: "admin" as PageKey, label: "后台", icon: Settings }] : base;
  }, [role]);

  const renderContent = () => {
    if (!user) return null;
    if (active === "knowledge") return <KnowledgeWarehouseView userId={userId} />;
    if (active === "courses") return role === "student" ? <StudentCourseView /> : <CourseManagementView role={role} />;
    if (active === "exams") return <ExamView role={role} />;
    if (active === "tasks") return <TaskView role={role} />;
    if (active === "profile") return <ProfileView userId={userId} />;
    if (active === "report") return <ReportView userId={userId} />;
    if (active === "settings") return <SettingsView />;
    if (active === "admin") return <AdminView />;

    return (
      <>
        {loading && <p className="dashboard-loading">加载中…</p>}
        {error && <p className="dashboard-loading">{error}</p>}
        <div className="dashboard-grid">
          <section className="study-card">
            <h2>学习趋势</h2>
            <div className="chart-box">
              <svg className="study-chart" viewBox="0 0 700 260" role="img" aria-label="学习趋势图">
                <polyline
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="4"
                  points={(dashboard?.summary.trend ?? []).map((item, index) => `${40 + index * 100},${220 - Math.min(item.minutes, 120) * 1.5}`).join(" ")}
                />
              </svg>
            </div>
            <div className="study-summary">
              <div><strong>{dashboard?.summary.today_study_minutes ?? 0}</strong><span>今日学习分钟</span></div>
              <div><strong>{dashboard?.summary.week_avg_minutes ?? 0}</strong><span>周均学习分钟</span></div>
              <div><strong>{dashboard?.summary.streak_days ?? 0}</strong><span>连续学习天数</span></div>
            </div>
          </section>

          <aside className="assistant-card">
            <div className="assistant-title"><div className="robot">🤖</div><h2>智能学习助手</h2></div>
            <div className="assistant-item">今日建议<span>先复习掌握度较低的知识点，再进入新知识点练习。</span></div>
            <div className="assistant-item">学习提醒<span>错题会自动进入复习计划，请按时完成复习。</span></div>
          </aside>

          {knowledgeCards.slice(0, 3).map((card) => (
            <article className="knowledge-card" key={card.knowledge_id}>
              <div className="knowledge-card-header"><h2>{card.name}</h2></div>
              <p><span>掌握度</span><strong>{card.mastery_percent}%</strong></p>
              <div className="progress-bar"><span style={{ width: `${card.mastery_percent}%` }} /></div>
              <button className="knowledge-start" type="button" onClick={() => setActive("knowledge")}>继续学习</button>
            </article>
          ))}

          <section className="path-card">
            <h2>学习路径</h2>
            <div className="path-list">
              {(dashboard?.learning_path ?? []).slice(0, 6).map((node, index) => (
                <div className="path-segment" key={node.knowledge_id}>
                  <div className={`path-node ${node.status}`}>
                    <span className="path-node-line">{node.name}</span>
                    <small>{Math.round(node.mastery * 100)}%</small>
                  </div>
                  {index < Math.min((dashboard?.learning_path?.length ?? 0), 6) - 1 && <span className="path-arrow">→</span>}
                </div>
              ))}
              {!dashboard?.learning_path?.length && <p className="path-empty">暂无学习路径数据</p>}
            </div>
          </section>
        </div>
      </>
    );
  };

  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <div className="dashboard-avatar">{user?.username?.slice(0, 1)?.toUpperCase() || "U"}</div>
        <nav className="dashboard-nav">
          {navItems.map(({ key, label, icon: Icon }) => (
            <button key={key} type="button" className={`dashboard-nav-item${active === key ? " active" : ""}`} onClick={() => setActive(key)} title={label}>
              <Icon size={20} />
            </button>
          ))}
        </nav>
        <button type="button" className="dashboard-logout" onClick={() => void logout()}><LogOut size={20} /></button>
      </aside>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <header className="dashboard-header">
            <div><h1>{pageTitle[active]}</h1><p>{user?.username} · {role}</p></div>
            <button type="button" className="dashboard-date"><CalendarDays size={18} /> {new Date().toLocaleDateString()}</button>
          </header>
          {renderContent()}
        </div>
      </main>
    </div>
  );
}
