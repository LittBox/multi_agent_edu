import { useEffect, useState } from "react";
import { useAuthStore } from "../stores";
import "../styles/pages/SettingsView.css";

interface EditProfileViewProps {
  onBack?: () => void;
  onSaved?: () => void;
}

export default function EditProfileView({
  onBack,
  onSaved,
}: EditProfileViewProps) {
  const { user, updateCurrentUser } = useAuthStore();

  const [username, setUsername] = useState(user?.username ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [saving, setSaving] = useState(false);
  const [localMessage, setLocalMessage] = useState("");
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    setUsername(user?.username ?? "");
    setEmail(user?.email ?? "");
  }, [user?.username, user?.email]);

  const saveProfile = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const nextUsername = username.trim();
    const nextEmail = email.trim();

    if (!nextUsername) {
      setLocalError("用户名不能为空");
      setLocalMessage("");
      return;
    }

    setSaving(true);
    setLocalError("");
    setLocalMessage("");

    try {
      await updateCurrentUser({
        username: nextUsername,
        email: nextEmail || null,
      });

      setLocalMessage("资料保存成功");
      onSaved?.();
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : "资料保存失败");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="settings-card">
      <div className="settings-card__header">
        <div>
          <h2>修改个人资料</h2>
          <p>修改用户名、邮箱等基础信息</p>
        </div>

        {onBack && (
          <button type="button" onClick={onBack}>
            返回
          </button>
        )}
      </div>

      <form className="settings-form" onSubmit={saveProfile}>
        <label>
          用户名
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="请输入用户名"
          />
        </label>

        <label>
          邮箱
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="请输入邮箱"
          />
        </label>

        {localMessage && <p className="settings-success">{localMessage}</p>}
        {localError && <p className="settings-error">{localError}</p>}

        <button type="submit" disabled={saving || !username.trim()}>
          {saving ? "保存中..." : "保存资料"}
        </button>
      </form>
    </section>
  );
}