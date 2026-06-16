import { useEffect, useState, type ReactNode } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";

import "./App.css";

import AuthPage from "./pages/AuthPage";
import LoginFormPage from "./pages/LoginFormPage";
import DashboardPage from "./pages/DashboardPage";
import DashboardLayout, { type DashboardView, type UserRole } from "./components/DashboardLayout/DashboardLayout";
import CourseManagementView from "./pages/CourseManagementView";
import StudentCourseView from "./pages/StudentCourseView";
import KnowledgeWarehouseView from "./pages/KnowledgeWarehouseView";
import ProfileView from "./pages/ProfileView";
import SettingsView from "./pages/SettingsView";
import PracticePage from "./pages/PracticePage";
import TaskView from "./pages/TaskView";

import { useAuthStore } from "./stores/AuthStore";

const canAccess = (role: UserRole, allowedRoles: UserRole[]) => allowedRoles.includes(role);

function App() {
  const navigate = useNavigate();
  const { page, user, loading, initAuth, logout } = useAuthStore();
  const [showPractice, setShowPractice] = useState(false);
  const [practiceKnowledgeId, setPracticeKnowledgeId] = useState<number | undefined>();

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  if (loading) {
    return <div>Loading...</div>;
  }



  const handleNavigate = (view: DashboardView) => {
    const pathMap: Record<DashboardView, string> = {
      home: "/dashboard",
      users: "/admin/users",
      "admin-stats": "/dashboard",
      courses: "/teacher/courses",
      tasks: "/tasks",
      "student-courses": "/student/courses",
      warehouse: "/knowledge",
      profile: "/profile",
      settings: "/settings",
    };
    navigate(pathMap[view]);
  };

  const renderWithLayout = (activeView: DashboardView, allowedRoles: UserRole[], content: ReactNode) => {
    if (!user) {
      return <Navigate to="/login" replace />;
    }

    if (!canAccess(user.role, allowedRoles)) {
      return <Navigate to="/dashboard" replace />;
    }
    return (
      <>
        {showPractice && (
          <PracticePage
            userId={currentUserId}
            knowledgeId={practiceKnowledgeId}
            onClose={() => {
              setShowPractice(false);
              setPracticeKnowledgeId(undefined);
            }}
          />
        )}

        <DashboardLayout activeView={activeView} onNavigate={handleNavigate} onLogout={logout} role={user.role}>
          {content}
        </DashboardLayout>
      </>
    );
  };

  
  if (!user) {
    return (
      <Routes>
        <Route path="/" element={<AuthPage/>} />
        <Route path="/login" element={<LoginFormPage />} />
        <Route path="*" element={page === "login" ? <Navigate to="/login" replace /> : <Navigate to="/" replace />} />
      </Routes>
    );
  }
  const resolvedUserId = user?.id ?? user?.user_id;

  if (typeof resolvedUserId !== "number") {
    return <div>当前登录用户缺少用户ID，请检查登录接口或 /auth/me 返回值。</div>;
  }

  const currentUserId: number = resolvedUserId;
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<DashboardPage/>} />
      <Route path="/admin/users" element={renderWithLayout("users", ["admin"], <div className="course-management-view"><header className="course-header"><div><h1>人员管理</h1><p>管理员维护系统人员、角色与账号状态。</p></div></header><section className="course-card"><h2>用户列表</h2><p className="course-empty">人员管理接口待接入，但该入口仅管理员可见可访问。</p></section></div>)} />
      <Route path="/teacher/courses" element={renderWithLayout("courses", ["teacher"], <CourseManagementView role={user.role} />)} />
      <Route path="/student/courses" element={renderWithLayout("student-courses", ["student"], <StudentCourseView />)} />
      <Route path="/courses" element={<Navigate to={user.role === "teacher" ? "/teacher/courses" : user.role === "student" ? "/student/courses" : "/dashboard"} replace />} />
      <Route path="/knowledge" element={renderWithLayout("warehouse", ["teacher", "student"], <KnowledgeWarehouseView userId={currentUserId} />)} />
      <Route path="/tasks" element={renderWithLayout("tasks", ["teacher", "student"], <TaskView role={user.role} />)} />
      <Route path="/profile" element={renderWithLayout("profile", ["teacher", "student"], <ProfileView userId={currentUserId} />)} />
      <Route path="/settings" element={renderWithLayout("settings", ["admin", "teacher", "student"], <SettingsView />)} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
