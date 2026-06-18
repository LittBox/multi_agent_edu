import { useState } from "react";
import { useUserStore } from "../stores";
import "../styles/pages/SettingsView.css";

interface ChangePasswordViewProps {
  onBack?: () => void;
  onSaved?: () => void;
}

export default function ChangePasswordView({
  onBack,
  onSaved,
}: ChangePasswordViewProps) {
  const { changePassword, message, error, clearMessage, clearError } =
    useUserStore();

  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [localError, setLocalError] = useState("");

  const savePassword = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!oldPassword || !newPassword) {
      setLocalError("请填写原密码和新密码");
      return;
    }

    setSaving(true);
    setLocalError("");
    clearMessage();
    clearError();

    try {
      await changePassword({
        old_password: oldPassword,
        new_password: newPassword,
      });

      setOldPassword("");
      setNewPassword("");
      onSaved?.();
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : "密码修改失败");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="settings-card">
      <div className="settings-card__header">
        <div>
          <h2>修改密码</h2>
          <p>修改当前账号的登录密码</p>
        </div>

        {onBack && (
          <button type="button" onClick={onBack}>
            返回
          </button>
        )}
      </div>

      <form className="settings-form" onSubmit={savePassword}>
        <label>
          原密码
          <input
            type="password"
            value={oldPassword}
            onChange={(event) => setOldPassword(event.target.value)}
            placeholder="请输入原密码"
          />
        </label>

        <label>
          新密码
          <input
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            placeholder="请输入新密码"
          />
        </label>

        {message && <p className="settings-success">{message}</p>}
        {error && <p className="settings-error">{error}</p>}
        {localError && <p className="settings-error">{localError}</p>}

        <button type="submit" disabled={saving || !oldPassword || !newPassword}>
          {saving ? "修改中..." : "修改密码"}
        </button>
      </form>
    </section>
  );
}