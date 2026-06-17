import { useEffect, useState } from "react";
import { useAuthStore, useUserStore } from "../stores";
import "../styles/pages/SettingsView.css";
import { useRoleStore } from "../stores/RoleStore";

/** 设置页：更新基础资料和修改密码。 */
export default function SettingsView() {
  const { user, updateCurrentUser } = useAuthStore();
  const { changePassword, message, error } = useUserStore();
  const [username, setUsername] = useState(user?.username ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [localMessage, setLocalMessage] = useState("");
  const {
    studentInfo,
    loading: studentLoading,
    error: studentError,
    getMyStudentInfo,
    updateMyStudentInfo,
  } = useRoleStore();

  const [studentNo, setStudentNo] = useState("");
  const [studentName, setStudentName] = useState("");
  const [studentMajor, setStudentMajor] = useState("");
  const [studentGrade, setStudentGrade] = useState("");
  const [studentClassName, setStudentClassName] = useState("");
  const [studentMessage, setStudentMessage] = useState("");
  
  useEffect(() => {
    getMyStudentInfo();
  }, [getMyStudentInfo]);

  useEffect(() => {
  if (!studentInfo) return;
    setStudentNo(studentInfo.student_no ?? "");
    setStudentName(studentInfo.student_name ?? "");
    setStudentMajor(studentInfo.major ?? "");
    setStudentGrade(studentInfo.grade != null ? String(studentInfo.grade) : "");
    setStudentClassName(studentInfo.class_name ?? "");
  }, [studentInfo]);

  const handleUpdateStudentInfo = async () => {
    await updateMyStudentInfo({
      student_no: studentNo,
      student_name: studentName,
      major: studentMajor,
      grade: studentGrade ? Number(studentGrade) : null,
      class_name: studentClassName,
    });

    setStudentMessage("学生资料更新成功");
  };

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

  const saveStudentProfile = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    await handleUpdateStudentInfo();
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

      
      {user?.role === "student" && (  
       <section className="settings-card">
          <h2>学生资料更新</h2>

          <form className="settings-form" onSubmit={saveStudentProfile}>
            <label>
              学号
              <input
                value={studentNo}
                onChange={(e) => setStudentNo(e.target.value)}
              />
            </label>

            <label>
              姓名
              <input
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
              />
            </label>

            <label>
              专业
              <input
                value={studentMajor}
                onChange={(e) => setStudentMajor(e.target.value)}
              />
            </label>

            <label>
              年级
              <input
                value={studentGrade}
                onChange={(e) => setStudentGrade(e.target.value)}
              />
            </label>

            <label>
              班级
              <input
                value={studentClassName}
                onChange={(e) => setStudentClassName(e.target.value)}
              />
            </label>

            {studentMessage && <p className="settings-success">{studentMessage}</p>}
            {studentError && <p className="settings-error">{studentError}</p>}

            <button
              type="submit"
              disabled={
                studentLoading ||
                !studentNo ||
                !studentName ||
                !studentMajor ||
                !studentGrade ||
                !studentClassName
              }
            >
              {studentLoading ? "更新中..." : "更新资料"}
            </button>
          </form>
        </section>
      )}
    </div>
  );
}
