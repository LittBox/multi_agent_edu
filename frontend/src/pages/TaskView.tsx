import { useEffect, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { useTaskStore } from "../stores";
import type { UserRole } from "../api/auth";
import "../styles/pages/CourseManagementView.css";

interface TaskViewProps { role: UserRole; }

/** 作业页：上方已发布作业，下方我的提交；教师额外显示作业题库。 */
export default function TaskView({ role }: TaskViewProps) {
  const { bank, releases, mySubmissions, answers, loading, error, message, setAnswer, loadBank, createBank, releaseTask, loadReleases, submitTask, loadMySubmissions } = useTaskStore();
  const [courseId, setCourseId] = useState("");
  const [content, setContent] = useState("");

  const refresh = async () => {
    await loadReleases();
    if (role === "teacher" || role === "admin") await loadBank();
    if (role === "student") await loadMySubmissions();
  };
  useEffect(() => { void refresh(); }, [role]);

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!courseId || !content.trim()) return;
    await createBank({ course_id: Number(courseId), task_type: "homework", task_content: content.trim() });
    setCourseId(""); setContent("");
  };

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div><h1>作业中心</h1><p>上方展示已发布作业，下方展示学生自己的作业进度。</p></div>
        <div className="course-header-actions"><button className="course-btn ghost" type="button" onClick={() => void refresh()}><RefreshCw size={16} />刷新</button></div>
      </header>
      {message && <p className="course-empty">{message}</p>}
      {error && <p className="course-empty">{error}</p>}

      {(role === "teacher" || role === "admin") && (
        <section className="course-card">
          <h2>作业题库</h2>
          <form className="course-form" onSubmit={create}>
            <label>课程 ID<input value={courseId} onChange={(e) => setCourseId(e.target.value)} /></label>
            <label>作业内容<textarea value={content} onChange={(e) => setContent(e.target.value)} /></label>
            <button className="course-btn primary" type="submit"><Plus size={16} />创建作业</button>
          </form>
          <div className="course-list course-grid-list">
            {bank.map((item) => <article className="course-item course-mini-card" key={item.task_id}><div><h3>课程 #{item.course_id}</h3><p>{item.task_content}</p><span>{item.task_type}</span></div><div className="course-item-actions"><button type="button" onClick={() => void releaseTask({ task_id: item.task_id })}>发布</button></div></article>)}
          </div>
        </section>
      )}

      <section className="course-card">
        <h2>已发布作业</h2>
        {loading && <p className="course-empty">加载中…</p>}
        <div className="course-list course-grid-list">
          {releases.map((item) => (
            <article className="course-item course-mini-card" key={item.task_publish_id}>
              <div><h3>作业 #{item.task_publish_id}</h3><p>{item.task_content || "暂无内容"}</p><span>课程：{item.course_id ?? "-"}</span><p>截止：{item.deadline ? new Date(item.deadline).toLocaleString() : "未设置"}</p></div>
              {role === "student" && <div className="course-item-actions"><textarea value={answers[item.task_publish_id] ?? ""} onChange={(e) => setAnswer(item.task_publish_id, e.target.value)} placeholder="填写作业答案" /><button type="button" onClick={() => void submitTask(item.task_publish_id)}>提交</button></div>}
            </article>
          ))}
        </div>
      </section>

      {role === "student" && (
        <section className="course-card">
          <h2>我的作业进度</h2>
          <div className="course-list course-grid-list">
            {mySubmissions.map((item) => <article className="course-item course-mini-card" key={item.submit_id}><div><h3>提交 #{item.submit_id}</h3><p>{item.answer_content}</p><span>得分：{item.score ?? "待评分"}</span><p>评语：{item.comment || "暂无"}</p></div></article>)}
          </div>
        </section>
      )}
    </div>
  );
}
