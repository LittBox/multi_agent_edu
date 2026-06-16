import { useState } from "react";
import { useAuthStore } from "../stores";
import type { UserRole } from "../api/auth";
import "../styles/pages/LoginFormPage.css";

/** 登录页：只负责登录/注册表单和角色选择，认证状态交给 AuthStore 管理。 */
export default function LoginFormPage() {
  const { login, register, loading, error, clearError } = useAuthStore();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [role, setRole] = useState<UserRole>("student");
  const [username, setUsername] = useState("");
  const [pwd, setPwd] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    clearError();
    setMessage("");

    if (!username.trim() || !pwd.trim()) {
      setMessage("请输入用户名和密码");
      return;
    }

    if (mode === "register") {
      await register({ username: username.trim(), pwd, role, email: email.trim() || null });
      setMessage("注册成功，请登录");
      setMode("login");
      setPwd("");
      return;
    }

    await login(username.trim(), pwd, role);
  };

  return (
    <div className="login-wrapper">
      <div className="login-container">
        <h1>{mode === "login" ? "欢迎登录智能学习系统" : "创建学习账号"}</h1>

        <div className="role-switcher" aria-label="选择登录角色">
          {(["admin", "teacher", "student"] as UserRole[]).map((item) => (
            <button
              key={item}
              type="button"
              className={`role-switcher-item${role === item ? " is-active" : ""}`}
              onClick={() => setRole(item)}
            >
              {item === "admin" ? "管理员" : item === "teacher" ? "教师" : "学生"}
            </button>
          ))}
          <span className="role-switcher-indicator" data-role={role} />
        </div>

        <form className="login-form" onSubmit={submit}>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="用户名" />
          <input value={pwd} onChange={(e) => setPwd(e.target.value)} placeholder="密码" type="password" />
          {mode === "register" && (
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="邮箱，可选" />
          )}
          {message && <p className="login-success">{message}</p>}
          {error && <p className="login-error">{error}</p>}
          <button type="submit" disabled={loading}>{loading ? "处理中…" : mode === "login" ? "登录" : "注册"}</button>
        </form>

        <div className="login-divider" />
        <div className="login-actions">
          <span className="login-link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "没有账号？去注册" : "已有账号？去登录"}
          </span>
          <span className="login-link register">当前角色：{role}</span>
        </div>
      </div>
      <ul className="bg-bubbles">{Array.from({ length: 10 }).map((_, index) => <li key={index} />)}</ul>
    </div>
  );
}
