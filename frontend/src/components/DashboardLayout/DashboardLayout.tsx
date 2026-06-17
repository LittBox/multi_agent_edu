import type { ReactNode } from "react";
import {
  House,
  BookOpen,
  User,
  ChartColumn,
  Settings,
  LogOut,
  GraduationCap,
  ClipboardList,
} from "lucide-react";
import Tooltip from "@mui/material/Tooltip";
import "../../styles/pages/DashboardPage.css";
import "../../styles/components/DashboardLayout.css";

export type UserRole = "admin" | "teacher" | "student";

export type DashboardView =
  | "home"
  | "users"
  | "admin-stats"
  | "warehouse"
  | "profile"
  | "settings"
  | "courses"
  | "student-courses"
  | "tasks";

interface DashboardLayoutProps {
  activeView: DashboardView;
  onNavigate: (view: DashboardView) => void;
  onLogout: () => void;
  children: ReactNode;
  role: UserRole;
}

const MENU_CONFIG: Array<{
  view: DashboardView;
  tooltip: string;
  icon: typeof House;
  roles: UserRole[];
}> = [
  { view: "home", tooltip: "首页", icon: House, roles: ["student"] },
  { view: "users", tooltip: "人员管理", icon: User, roles: ["admin"] },
  { view: "admin-stats", tooltip: "人员统计", icon: ChartColumn, roles: ["admin"] },
  { view: "courses", tooltip: "课程管理", icon: GraduationCap, roles: ["teacher"] },
  { view: "tasks", tooltip: "作业题库", icon: ClipboardList, roles: ["teacher", "student"] },
  { view: "student-courses", tooltip: "我的课程", icon: GraduationCap, roles: ["student"] },
  { view: "warehouse", tooltip: "知识仓库", icon: BookOpen, roles: ["teacher", "student"] },
  { view: "profile", tooltip: "个人中心", icon: User, roles: ["teacher", "student"] },
  { view: "settings", tooltip: "设置", icon: Settings, roles: ["admin", "teacher", "student"] },
];

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  activeView,
  onNavigate,
  onLogout,
  children,
  role,
}) => {
  const visibleNavItems = MENU_CONFIG.filter((item) => item.roles.includes(role));

  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <div className="dashboard-avatar" aria-hidden>
          <User size={44} strokeWidth={1.5} />
        </div>

        <nav className="dashboard-nav">
          {visibleNavItems.map(({ view, tooltip, icon: Icon }) => (
            <Tooltip key={view} title={tooltip} placement="right" arrow>
              <button
                type="button"
                className={`dashboard-nav-item${activeView === view ? " active" : ""}`}
                onClick={() => onNavigate(view)}
                aria-label={tooltip}
              >
                <Icon size={24} />
              </button>
            </Tooltip>
          ))}
        </nav>

        <Tooltip title="退出登录" placement="right" arrow>
          <button type="button" className="dashboard-logout" onClick={onLogout} aria-label="退出登录">
            <LogOut size={22} />
          </button>
        </Tooltip>
      </aside>

      <main className="dashboard-main">
        <div className="dashboard-content">{children}</div>
      </main>
    </div>
  );
};

export default DashboardLayout;
