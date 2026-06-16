import { useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { useExamStore } from "../stores";
import type { UserRole } from "../api/auth";
import "../styles/pages/CourseManagementView.css";

interface ExamViewProps { role: UserRole; }

/** 考试页：已发布考试、正在考试、我的提交记录上下分区。 */
export default function ExamView({ role }: ExamViewProps) {
  const { exams, currentExam, questions, answers, mySubmissions, loading, error, message, loadExams, createExam, startExam, setAnswer, submitExam, loadMySubmissions } = useExamStore();
  const [title, setTitle] = useState("");
  const [courseId, setCourseId] = useState("");

  const refresh = async () => {
    await loadExams();
    if (role === "student") await loadMySubmissions();
  };
  useEffect(() => { void refresh(); }, [role]);

  const visibleExams = useMemo(() => role === "student" ? exams.filter((item) => ["published", "active", "ongoing"].includes(item.status)) : exams, [exams, role]);

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!title.trim() || !courseId) return;
    await createExam({ title: title.trim(), course_id: Number(courseId), duration_minutes: 60, exam_type: "quiz", status: "published" });
    setTitle(""); setCourseId("");
  };

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div><h1>考试中心</h1><p>上方展示已发布考试，下方展示正在进行的考试和我的记录。</p></div>
        <div className="course-header-actions"><button className="course-btn ghost" type="button" onClick={() => void refresh()}><RefreshCw size={16} />刷新</button></div>
      </header>
      {message && <p className="course-empty">{message}</p>}
      {error && <p className="course-empty">{error}</p>}

      {(role === "teacher" || role === "admin") && (
        <section className="course-card">
          <h2>创建考试</h2>
          <form className="course-form" onSubmit={create}>
            <label>考试标题<input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
            <label>课程 ID<input value={courseId} onChange={(e) => setCourseId(e.target.value)} /></label>
            <button className="course-btn primary" type="submit"><Plus size={16} />创建并发布</button>
          </form>
        </section>
      )}

      <section className="course-card">
        <h2>{role === "student" ? "已发布考试" : "考试列表"}</h2>
        {loading && <p className="course-empty">加载中…</p>}
        {!loading && visibleExams.length === 0 && <p className="course-empty">暂无考试</p>}
        <div className="course-list course-grid-list">
          {visibleExams.map((exam) => (
            <article className="course-item course-mini-card" key={exam.exam_id}>
              <div><h3>{exam.title}</h3><p>课程 ID：{exam.course_id} · {exam.duration_minutes} 分钟</p><span>{exam.exam_type} · {exam.status}</span></div>
              {role === "student" && <div className="course-item-actions"><button type="button" onClick={() => void startExam(exam.exam_id)}>进入考试</button></div>}
            </article>
          ))}
        </div>
      </section>

      {role === "student" && (
        <section className="course-card">
          <h2>正在进行中的考试</h2>
          {!currentExam && <p className="course-empty">点击上方考试卡片开始答题。</p>}
          {currentExam && (
            <div className="course-list">
              <article className="course-item"><div><h3>{currentExam.title}</h3><p>考试时长：{currentExam.duration_minutes} 分钟</p></div></article>
              {questions.length === 0 && <p className="course-empty">当前试卷暂无题目。</p>}
              {questions.map((q, index) => (
                <article className="course-item" key={q.exam_question_id}>
                  <div>
                    <h3>{index + 1}. {q.stem}</h3>
                    <p>A. {q.option_a ?? "-"}</p><p>B. {q.option_b ?? "-"}</p><p>C. {q.option_c ?? "-"}</p><p>D. {q.option_d ?? "-"}</p>
                    <input value={answers[String(q.question_id)] ?? ""} onChange={(e) => setAnswer(q.question_id, e.target.value)} placeholder="请输入答案" />
                  </div>
                </article>
              ))}
              <button className="course-btn primary" type="button" onClick={() => void submitExam(currentExam.exam_id)}>提交试卷</button>
            </div>
          )}
        </section>
      )}

      {role === "student" && (
        <section className="course-card">
          <h2>我的考试记录</h2>
          <div className="course-list course-grid-list">
            {mySubmissions.map((item) => <article className="course-item course-mini-card" key={item.exam_submit_id}><div><h3>考试 #{item.exam_id}</h3><p>得分：{item.total_score ?? "待评分"}</p><span>{item.teacher_comment || "暂无评语"}</span></div></article>)}
          </div>
        </section>
      )}
    </div>
  );
}
