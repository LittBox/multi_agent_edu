import { useState } from "react";
import DashboardLayout, {
  type DashboardView,
} from "../components/DashboardLayout/DashboardLayout";
import HomeDashboardView from "./HomeDashboardView";
import KnowledgeWarehouseView from "./KnowledgeWarehouseView";
import ProfileView from "./ProfileView";
import ReportView from "./ReportView";
import SettingsView from "./SettingsView";
import PracticePage from "./PracticePage";
import "../styles/pages/DashboardPage.css";
import "../styles/pages/KnowledgeWarehousePage.css";
import "../styles/pages/ProfileView.css";
import "../styles/pages/ReportView.css";
import "../styles/pages/SettingsView.css";

interface DashboardPageProps {
  userId: number;
  username?: string;
  onLogout: () => void;
}

const DashboardPage: React.FC<DashboardPageProps> = ({
  userId,
  username,
  onLogout,
}) => {
  const [activeView, setActiveView] = useState<DashboardView>("home");
  const [showPractice, setShowPractice] = useState(false);
  const [practiceKnowledgeId, setPracticeKnowledgeId] = useState<
    number | undefined
  >();

  const openPractice = (knowledgeId?: number) => {
    setPracticeKnowledgeId(knowledgeId);
    setShowPractice(true);
  };

  const handleNavigate = (view: DashboardView) => {
    setActiveView(view);
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
        activeView={activeView}
        onNavigate={handleNavigate}
        onLogout={onLogout}
      >
        {activeView === "home" && (
          <HomeDashboardView
            userId={userId}
            username={username}
            onPractice={() => openPractice()}
          />
        )}

        {activeView === "warehouse" && (
          <KnowledgeWarehouseView
            userId={userId}
            onPractice={openPractice}
          />
        )}

        {activeView === "profile" && <ProfileView userId={userId} />}

        {activeView === "report" && <ReportView userId={userId} />}

        {activeView === "settings" && <SettingsView />}
      </DashboardLayout>
    </>
  );
};

export default DashboardPage;
