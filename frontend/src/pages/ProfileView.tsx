import { useEffect } from "react";
import { UserRound } from "lucide-react";
import { useUserStore } from "../stores";
import "../styles/pages/ProfileView.css";

interface ProfileViewProps { userId: number; }

/** 个人主页：展示用户资料和学习统计。 */
export default function ProfileView({ userId }: ProfileViewProps) {
  const { profile, loading, error, loadProfile } = useUserStore();

  useEffect(() => { if (userId) void loadProfile(userId); }, [userId, loadProfile]);

  return (
    <div className="profile-view">
      <header className="profile-header">
        <div className="profile-avatar-lg"><UserRound size={48} /></div>
        <div><h1>{profile?.user.username || "个人主页"}</h1><p>{profile?.user.email || "暂无邮箱"}</p></div>
      </header>

      {loading && <p className="profile-loading">加载中…</p>}
      {error && <p className="profile-loading">{error}</p>}

      <div className="profile-stats-grid">
        <div className="profile-stat"><strong>{profile?.stats.total_answers ?? 0}</strong><span>答题总数</span></div>
        <div className="profile-stat"><strong>{profile?.stats.correct_answers ?? 0}</strong><span>正确题数</span></div>
        <div className="profile-stat"><strong>{Math.round((profile?.stats.accuracy ?? 0) * 100)}%</strong><span>正确率</span></div>
        <div className="profile-stat"><strong>{profile?.stats.mastered_count ?? 0}</strong><span>已掌握知识点</span></div>
      </div>

      <section className="profile-card">
        <h2>基础信息</h2>
        <dl>
          <div><dt>用户 ID</dt><dd>{profile?.user.user_id ?? userId}</dd></div>
          <div><dt>用户名</dt><dd>{profile?.user.username ?? "-"}</dd></div>
          <div><dt>角色</dt><dd>{profile?.user.role ?? "-"}</dd></div>
          <div><dt>状态</dt><dd>{profile?.user.status ?? "-"}</dd></div>
          <div><dt>加入时间</dt><dd>{profile?.joined_at ? new Date(profile.joined_at).toLocaleString() : "-"}</dd></div>
        </dl>
      </section>
    </div>
  );
}
