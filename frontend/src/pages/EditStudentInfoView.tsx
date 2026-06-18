import { useEffect, useState } from "react";
import { useRoleStore } from "../stores/RoleStore";
import "../styles/pages/SettingsView.css";

interface EditStudentInfoViewProps {
  onBack?: () => void;
  onSaved?: () => void;
}

export default function EditStudentInfoView({
  onBack,
  onSaved,
}: EditStudentInfoViewProps) {
  const {
    studentInfo,
    loading,
    error,
    getMyStudentInfo,
    updateMyStudentInfo,
  } = useRoleStore();

  const [studentNo, setStudentNo] = useState("");
  const [studentName, setStudentName] = useState("");
  const [studentMajor, setStudentMajor] = useState("");
  const [studentGrade, setStudentGrade] = useState("");
  const [studentClassName, setStudentClassName] = useState("");
  const [localMessage, setLocalMessage] = useState("");
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    void getMyStudentInfo();
  }, [getMyStudentInfo]);

  useEffect(() => {
    if (!studentInfo) return;

    setStudentNo(studentInfo.student_no ?? "");
    setStudentName(studentInfo.student_name ?? "");
    setStudentMajor(studentInfo.major ?? "");
    setStudentGrade(
      studentInfo.grade != null ? String(studentInfo.grade) : ""
    );
    setStudentClassName(studentInfo.class_name ?? "");
  }, [studentInfo]);

  const saveStudentInfo = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (
      !studentNo.trim() ||
      !studentName.trim() ||
      !studentMajor.trim() ||
      !studentGrade.trim() ||
      !studentClassName.trim()
    ) {
      setLocalError("请完整填写学生资料");
      setLocalMessage("");
      return;
    }

    setLocalError("");
    setLocalMessage("");

    try {
      await updateMyStudentInfo({
        student_no: studentNo.trim(),
        student_name: studentName.trim(),
        major: studentMajor.trim(),
        grade: Number(studentGrade),
        class_name: studentClassName.trim(),
      });

      setLocalMessage("学生资料更新成功");
      onSaved?.();
    } catch (error) {
      setLocalError(error instanceof Error ? error.message : "学生资料更新失败");
    }
  };

  return (
    <section className="settings-card">
      <div className="settings-card__header">
        <div>
          <h2>学生资料</h2>
          <p>维护学号、专业、年级、班级等信息</p>
        </div>

        {onBack && (
          <button type="button" onClick={onBack}>
            返回
          </button>
        )}
      </div>

      <form className="settings-form" onSubmit={saveStudentInfo}>
        <label>
          学号
          <input
            value={studentNo}
            onChange={(event) => setStudentNo(event.target.value)}
            placeholder="请输入学号"
          />
        </label>

        <label>
          姓名
          <input
            value={studentName}
            onChange={(event) => setStudentName(event.target.value)}
            placeholder="请输入姓名"
          />
        </label>

        <label>
          专业
          <input
            value={studentMajor}
            onChange={(event) => setStudentMajor(event.target.value)}
            placeholder="请输入专业"
          />
        </label>

        <label>
          年级
          <input
            value={studentGrade}
            onChange={(event) => setStudentGrade(event.target.value)}
            placeholder="请输入年级"
          />
        </label>

        <label>
          班级
          <input
            value={studentClassName}
            onChange={(event) => setStudentClassName(event.target.value)}
            placeholder="请输入班级"
          />
        </label>

        {localMessage && <p className="settings-success">{localMessage}</p>}
        {error && <p className="settings-error">{error}</p>}
        {localError && <p className="settings-error">{localError}</p>}

        <button
          type="submit"
          disabled={
            loading ||
            !studentNo.trim() ||
            !studentName.trim() ||
            !studentMajor.trim() ||
            !studentGrade.trim() ||
            !studentClassName.trim()
          }
        >
          {loading ? "更新中..." : "更新资料"}
        </button>
      </form>
    </section>
  );
}