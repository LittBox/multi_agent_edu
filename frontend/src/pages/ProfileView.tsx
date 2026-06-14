import { useEffect, useState } from "react";
import { User as UserIcon, Award, Target, BookOpen } from "lucide-react";
import { fetchUserProfile, type UserProfile } from "../api/user";
import "../styles/pages/ProfileView.css";

interface ProfileViewProps {
  userId: number;
}

const ROLE_LABELS: Record<string, string> = {
  admin: "管理员",
  teacher: "教师",
  student: "学生",
};

const ProfileView: React.FC<ProfileViewProps> = ({ userId }) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserProfile(userId)
      .then(setProfile)
      .catch(() => setProfile(null))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return <p className="profile-loading">加载中…</p>;
  }

  if (!profile) {
    return <p className="profile-loading">无法加载个人资料</p>;
  }

  const { user, stats, joined_at } = profile;
  const joinedDate = new Date(joined_at).toLocaleDateString("zh-CN");

  return (
    <div className="profile-view">
      <header className="profile-header">
        <div className="profile-avatar-lg">
          <UserIcon size={56} strokeWidth={1.2} />
        </div>
        <div>
          <h1>{user.username}</h1>
          <p>注册于 {joinedDate}</p>
        </div>
      </header>

      <div className="profile-stats-grid">
        <div className="profile-stat">
          <BookOpen size={22} />
          <strong>{stats.total_answers}</strong>
          <span>累计答题</span>
        </div>
        <div className="profile-stat">
          <Target size={22} />
          <strong>{(stats.accuracy * 100).toFixed(1)}%</strong>
          <span>总正确率</span>
        </div>
        <div className="profile-stat">
          <Award size={22} />
          <strong>{stats.mastered_count}</strong>
          <span>已掌握知识点</span>
        </div>
        <div className="profile-stat">
          <BookOpen size={22} />
          <strong>{stats.knowledge_points_tracked}</strong>
          <span>追踪知识点</span>
        </div>
      </div>

      <section className="profile-card">
        <h2>账号信息</h2>
        <dl>
          <div>
            <dt>用户名</dt>
            <dd>{user.username}</dd>
          </div>
          <div>
            <dt>角色</dt>
            <dd>{ROLE_LABELS[user.role] ?? user.role}</dd>
          </div>
          <div>
            <dt>邮箱</dt>
            <dd>{user.email || "未设置"}</dd>
          </div>
        </dl>
      </section>
    </div>
  );
};

export default ProfileView;
