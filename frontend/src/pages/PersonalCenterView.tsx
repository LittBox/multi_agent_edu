import { useEffect, useMemo, useState } from "react";

import PersonalHeroCard from "../components/personal-center/PersonalHeroCard";
import LearnerProfileRadar from "../components/personal-center/LearnerProfileRadar";
import AccuracyTrendChart from "../components/personal-center/AccuracyTrendChart";
import WeakKnowledgeList from "../components/personal-center/WeakKnowledgeList";
import SubjectMasteryPanel from "../components/personal-center/SubjectMasteryPanel";

import { useAuthStore } from "../stores/AuthStore";
import { useUserStore } from "../stores/UserStore";
import { useEducationStore } from "../stores/EducationStore";
import { useRoleStore } from "../stores/RoleStore";
import EditProfileView from "./EditProfileView";
import ChangePasswordView from "./ChangePasswordView";
import EditStudentInfoView from "./EditStudentInfoView";
import "../styles/pages/PersonalCenterView.css";

type PersonalCenterMode =
  | "overview"
  | "edit-profile"
  | "change-password"
  | "edit-student";

export default function PersonalCenterView() {
  const [mode, setMode] = useState<PersonalCenterMode>("overview");

  const { user } = useAuthStore();

  const {
    profile,
    loading: profileLoading,
    error: profileError,
    loadProfile,
  } = useUserStore();

  const {
    report,
    loading: reportLoading,
    error: reportError,
    loadReport,
  } = useEducationStore();

  const { studentInfo, getMyStudentInfo } = useRoleStore();

  const userId = useMemo(() => {
    const rawUserId = user?.user_id ?? user?.id ?? 0;
    const parsedUserId = Number(rawUserId);

    return Number.isFinite(parsedUserId) ? parsedUserId : 0;
  }, [user?.id, user?.user_id]);

  const isStudent = user?.role === "student";
  const isLoading = profileLoading || reportLoading;
  const errorMessage = profileError || reportError;

  const welcomeName =
    studentInfo?.student_name ||
    profile?.user?.username ||
    user?.username ||
    "同学";

  useEffect(() => {
    if (!userId) return;

    void loadProfile(userId);
    void loadReport(userId);
  }, [loadProfile, loadReport, userId]);

  useEffect(() => {
    if (!isStudent) return;

    void getMyStudentInfo();
  }, [getMyStudentInfo, isStudent]);

  const handleEditProfile = () => {
    setMode("edit-profile");
  };

  const handleChangePassword = () => {
    setMode("change-password");
  };

  const handleEditStudent = () => {
    setMode("edit-student");
  };

  const handleBackToOverview = () => {
    setMode("overview");
  };

  if (!userId) {
    return (
      <main className="personal-center">
        <section className="personal-center__state">
          <h1>个人中心</h1>
          <p>暂时无法获取当前登录用户信息。</p>
        </section>
      </main>
    );
  }

  if (mode !== "overview") {
        return (
            <main className="personal-center">
            {mode === "edit-profile" && (
                <EditProfileView
                onBack={handleBackToOverview}
                onSaved={() => {
                    if (userId) {
                    void loadProfile(userId);
                    }

                    handleBackToOverview();
                }}
                />
            )}

            {mode === "change-password" && (
                <ChangePasswordView
                onBack={handleBackToOverview}
                onSaved={handleBackToOverview}
                />
            )}

            {mode === "edit-student" && isStudent && (
                <EditStudentInfoView
                onBack={handleBackToOverview}
                onSaved={() => {
                    void getMyStudentInfo();
                    handleBackToOverview();
                }}
                />
            )}

            {mode === "edit-student" && !isStudent && (
                <section className="personal-center__placeholder">
                <span>Unavailable</span>
                <h1>学生资料</h1>
                <p>当前账号不是学生角色，无法编辑学生资料。</p>
                </section>
            )}
            </main>
        );
    }

  return (
    <main className="personal-center">
      <header className="personal-center__header">
        <div>
          <h1>个人中心</h1>
          <p>欢迎回来，{welcomeName}！继续保持，你正在不断进步。</p>
        </div>

        {isLoading && <span>数据加载中...</span>}
      </header>

      {errorMessage && (
        <section className="personal-center__error">
          {String(errorMessage)}
        </section>
      )}

      <PersonalHeroCard
        userId={userId}
        authUser={user}
        profile={profile}
        studentInfo={studentInfo}
        onEditProfile={handleEditProfile}
        onChangePassword={handleChangePassword}
        onEditStudent={handleEditStudent}
      />

      <section className="personal-center__main-grid">
        <LearnerProfileRadar radarItems={report?.profile?.radar ?? []} />

        <AccuracyTrendChart dailyAccuracy={report?.daily_accuracy ?? []} />
      </section>

      <section className="personal-center__bottom-grid">
        <WeakKnowledgeList weakPoints={report?.weak_points ?? []} />

        <SubjectMasteryPanel subjectStats={report?.subject_stats ?? []} />
      </section>
    </main>
  );
}