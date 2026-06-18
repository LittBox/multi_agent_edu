import { UserRound } from "lucide-react";
import AccountActionList from "./AccountActionList";

type UserLike = {
  id?: number | string;
  user_id?: number | string;
  username?: string | null;
  email?: string | null;
  role?: string | null;
  status?: string | null;
};

type ProfileLike = {
  user?: UserLike | null;
  joined_at?: string | null;
};

type StudentInfoLike = {
  student_no?: string | null;
  student_name?: string | null;
  major?: string | null;
  grade?: number | string | null;
  class_name?: string | null;
};

interface PersonalHeroCardProps {
  userId: number;
  authUser?: UserLike | null;
  profile?: ProfileLike | null;
  studentInfo?: StudentInfoLike | null;
  onEditProfile: () => void;
  onChangePassword: () => void;
  onEditStudent: () => void;
}

const formatRole = (role?: string | null) => {
  if (role === "student") return "学生";
  if (role === "teacher") return "教师";
  if (role === "admin") return "管理员";
  return role || "-";
};

const formatStatus = (status?: string | null) => {
  if (status === "active") return "正常";
  if (status === "disabled") return "禁用";
  if (status === "inactive") return "未启用";
  return status || "-";
};

const formatDateTime = (value?: string | null) => {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString();
};

export default function PersonalHeroCard({
  userId,
  authUser,
  profile,
  studentInfo,
  onEditProfile,
  onChangePassword,
  onEditStudent,
}: PersonalHeroCardProps) {
  const profileUser = profile?.user ?? authUser ?? {};
  const role = profileUser.role ?? authUser?.role ?? null;

  const displayUserId = profileUser.user_id ?? profileUser.id ?? userId;
  const displayName =
    studentInfo?.student_name ||
    profileUser.username ||
    authUser?.username ||
    "未命名用户";

  const displayEmail = profileUser.email || authUser?.email || "暂无邮箱";

  return (
    <section className="personal-hero-card">
      <div className="personal-hero-card__identity">
        <div className="personal-hero-card__avatar" aria-hidden="true">
          <UserRound />
        </div>

        <div className="personal-hero-card__main">
          <div className="personal-hero-card__name-row">
            <h2>{displayName}</h2>
            <span>{formatRole(role)}</span>
          </div>

          <p>{displayEmail}</p>

          <dl className="personal-hero-card__meta">
            <div>
              <dt>用户 ID</dt>
              <dd>{displayUserId}</dd>
            </div>

            <div>
              <dt>加入时间</dt>
              <dd>{formatDateTime(profile?.joined_at)}</dd>
            </div>

            <div>
              <dt>账号状态</dt>
              <dd>{formatStatus(profileUser.status)}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="personal-hero-card__info">
        <div className="personal-hero-card__section-title">
          <h3>基础信息</h3>
          <span>Profile</span>
        </div>

        <dl>
          <div>
            <dt>用户名</dt>
            <dd>{profileUser.username || "-"}</dd>
          </div>

          <div>
            <dt>姓名</dt>
            <dd>{studentInfo?.student_name || "-"}</dd>
          </div>

          <div>
            <dt>学号</dt>
            <dd>{studentInfo?.student_no || "-"}</dd>
          </div>

          <div>
            <dt>专业</dt>
            <dd>{studentInfo?.major || "-"}</dd>
          </div>

          <div>
            <dt>年级</dt>
            <dd>{studentInfo?.grade ?? "-"}</dd>
          </div>

          <div>
            <dt>班级</dt>
            <dd>{studentInfo?.class_name || "-"}</dd>
          </div>
        </dl>
      </div>

      <div className="personal-hero-card__actions">
        <AccountActionList
          isStudent={role === "student"}
          onEditProfile={onEditProfile}
          onChangePassword={onChangePassword}
          onEditStudent={onEditStudent}
        />
      </div>
    </section>
  );
}