import { useState } from "react";
import { useAuthStore, useUserStore } from "../stores";
import "../styles/pages/SettingsView.css";

/** 设置页：更新基础资料和修改密码。 */
export default function SettingsView() {
  const { user, updateCurrentUser } = useAuthStore();
  const { changePassword, message, error } = useUserStore();
  const [username, setUsername] = useState(user?.username ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [localMessage, setLocalMessage] = useState("");

  const saveProfile = async (event: React.FormEvent) => {
    event.preventDefault();
    await updateCurrentUser({ username: username.trim(), email: email.trim() || null });
    setLocalMessage("资料保存成功");
  };

  const savePassword = async (event: React.FormEvent) => {
    event.preventDefault();
    await changePassword({ old_password: oldPassword, new_password: newPassword });
    setOldPassword(""); setNewPassword("");
  };

  return (
    <div className="settings-view">
      <section className="settings-card">
        <h2>个人资料</h2>
        <form className="settings-form" onSubmit={saveProfile}>
          <label>用户名<input value={username} onChange={(e) => setUsername(e.target.value)} /></label>
          <label>邮箱<input value={email ?? ""} onChange={(e) => setEmail(e.target.value)} /></label>
          {localMessage && <p className="settings-success">{localMessage}</p>}
          <button type="submit">保存资料</button>
        </form>
      </section>

      <section className="settings-card">
        <h2>修改密码</h2>
        <form className="settings-form" onSubmit={savePassword}>
          <label>原密码<input type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} /></label>
          <label>新密码<input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} /></label>
          {message && <p className="settings-success">{message}</p>}
          {error && <p className="settings-error">{error}</p>}
          <button type="submit" disabled={!oldPassword || !newPassword}>修改密码</button>
        </form>
      </section>
    </div>
  );
}
