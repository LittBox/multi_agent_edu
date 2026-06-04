import { useState } from "react";
import { changePassword } from "../api/user";
import "../styles/pages/SettingsView.css";

const SettingsView: React.FC = () => {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setMessage("");

    if (newPassword !== confirmPassword) {
      setError("两次输入的新密码不一致");
      return;
    }

    setLoading(true);
    try {
      await changePassword({
        old_password: oldPassword,
        new_password: newPassword,
      });
      setMessage("密码修改成功");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "修改失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-view">
      <header className="settings-header">
        <h1>设置</h1>
        <p>账号安全与偏好</p>
      </header>

      <section className="settings-card">
        <h2>修改密码</h2>
        <form className="settings-form" onSubmit={handleSubmit}>
          <label>
            当前密码
            <input
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
            />
          </label>
          <label>
            新密码
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={6}
            />
          </label>
          <label>
            确认新密码
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
            />
          </label>

          {message && <p className="settings-success">{message}</p>}
          {error && <p className="settings-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "提交中…" : "保存密码"}
          </button>
        </form>
      </section>
    </div>
  );
};

export default SettingsView;
