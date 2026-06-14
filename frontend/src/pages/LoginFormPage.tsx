import { useState } from "react";
import { useAuthStore } from "../stores/AuthStore";
import { register as apiRegister } from "../api/auth";
import "../styles/pages/LoginFormPage.css";
import GhostMouse from "../components/GhostMouse/GhostMouse";

const roleOptions = [
  { value: "admin", label: "管理员" },
  { value: "teacher", label: "教师" },
  { value: "student", label: "学生" },
] as const;

const LoginFormPage: React.FC = () => {
  const login = useAuthStore((state) => state.login);

  const [formMode, setFormMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<(typeof roleOptions)[number]["value"]>("admin");
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const switchToRegister = () => {
    setErrorMsg("");
    setUsername("");
    setPassword("");
    setFormMode("register");
  };

  const switchToLogin = () => {
    setErrorMsg("");
    setUsername("");
    setPassword("");
    setFormMode("login");
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    try {
      setErrorMsg("");

      if (formMode === "login") {
        await login(username, password, role);
        return;
      }

      await apiRegister({
        username,
        pwd: password,
        role,
      });

      setFormMode("login");
      setUsername("");
      setPassword("");
      setErrorMsg("");
      setSuccessMsg("注册成功，请登录");
    } catch (error) {
      const message = error instanceof Error ? error.message : "请求失败";
      setErrorMsg(message || (formMode === "login" ? "账号或密码错误" : "注册失败"));
    }
  };

  return (
    <div className="login-wrapper">
      <GhostMouse />

      <div className="login-container">
        <h1>{formMode === "login" ? "Welcome" : "Register"}</h1>

        <div className="role-switcher" role="tablist" aria-label="选择登录角色">
          <span
            className="role-switcher-indicator"
            data-role={role}
            aria-hidden="true"
          />
          {roleOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`role-switcher-item ${role === option.value ? "is-active" : ""}`}
              onClick={() => setRole(option.value)}
              role="tab"
              aria-selected={role === option.value}
            >
              {option.label}
            </button>
          ))}
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {errorMsg && <p className="login-error">{errorMsg}</p>}
          {successMsg && <p className="login-success">{successMsg}</p>}
          <button type="submit">{formMode === "login" ? "Login" : "Register"}</button>
        </form>

        <div className="login-divider"></div>

        <div className="login-actions">
          <span className="login-link" onClick={() => alert("忘记密码功能尚未实现")}>
            忘记密码？
          </span>

          {formMode === "login" ? (
            <span className="login-link register" onClick={switchToRegister}>
              立即注册
            </span>
          ) : (
            <span className="login-link register" onClick={switchToLogin}>
              已有账号？去登录
            </span>
          )}
        </div>
      </div>

      <ul className="bg-bubbles">
        {Array.from({ length: 10 }).map((_, index) => (
          <li key={index}></li>
        ))}
      </ul>
    </div>
  );
};

export default LoginFormPage;
