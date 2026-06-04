import type { ReactNode } from "react";
import {
  House,
  BookOpen,
  User,
  ChartColumn,
  Settings,
  LogOut,
} from "lucide-react";
import "../../styles/pages/DashboardPage.css";
import "../../styles/components/DashboardLayout.css";
import Tooltip from "@mui/material/Tooltip"
import { view } from "motion/react-m";
export type DashboardView =
  | "home"
  | "warehouse"
  | "profile"
  | "report"
  | "settings";

interface DashboardLayoutProps {
  activeView: DashboardView;
  onNavigate: (view: DashboardView) => void;
  onLogout: () => void;
  children: ReactNode;
}

const NAV_ITEMS: Array<{
  view: DashboardView;
  label: string;
  tooltip: string;
  icon: typeof House;
}> = [
  { view: "home", tooltip:"首页", label: "", icon: House },
  { view: "warehouse", tooltip:"知识仓库", label: "", icon: BookOpen },
  { view: "profile", tooltip:"个人中心", label: "", icon: User },
  { view: "report", tooltip:"学习分析报告", label: "", icon: ChartColumn },
  { view: "settings", tooltip:"设置", label: "", icon: Settings },
];

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  activeView,
  onNavigate,
  onLogout,
  children,
}) => {
  return (
    <div className="dashboard-page">
      <aside className="dashboard-sidebar">
        <div className="dashboard-avatar" aria-hidden>
          <User size={44} strokeWidth={1.5} />
        </div>

        <nav className="dashboard-nav">
          {NAV_ITEMS.map(({ view, tooltip, icon: Icon }) => (
            <Tooltip
              key={view}
              title={tooltip}
              placement="right"
              arrow
            >
              <button
                type="button"
                className={`dashboard-nav-item${
                  activeView === view ? " active" : ""
                }`}
                onClick={() => onNavigate(view)}
              >
                <Icon size={24} />
              </button>
            </Tooltip>
          ))}
        </nav>

        <Tooltip
              key="logout"
              title="退出登录"
              placement="right"
              arrow
            >
          <button type="button" className="dashboard-logout" onClick={onLogout}>
            <LogOut size={22} />
          </button>
        </Tooltip>
      </aside>

      <main className="dashboard-main">
        <div className="dashboard-content">
          {children}
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
