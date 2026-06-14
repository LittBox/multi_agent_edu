import { useEffect, useState } from "react";
import { taskApi, type TaskBankItem, type TaskReleaseItem, type TaskSubmissionItem } from "../api/tasks";
import "../styles/pages/CourseManagementView.css";

interface TaskViewProps {
  role: "admin" | "teacher" | "student";
}

export default function TaskView({ role }: TaskViewProps) {
  const [bank, setBank] = useState<TaskBankItem[]>([]);
  const [releases, setReleases] = useState<TaskReleaseItem[]>([]);
  const [submissions, setSubmissions] = useState<TaskSubmissionItem[]>([]);
  const [courseId, setCourseId] = useState("");
  const [content, setContent] = useState("");
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [message, setMessage] = useState("");

  const load = async () => {
    try {
      setReleases(await taskApi.listReleases());
      if (role === "teacher" || role === "admin") {
        setBank(await taskApi.listBank());
      }
      if (role === "student") {
        setSubmissions(await taskApi.mySubmissions());
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "加载失败");
    }
  };

  useEffect(() => {
    void load();
  }, [role]);

  const createTask = async () => {
    if (!courseId || !content.trim()) return;
    await taskApi.createBank({ course_id: Number(courseId), task_type: "homework", task_content: content.trim() });
    setCourseId("");
    setContent("");
    await load();
  };

  const releaseTask = async (taskId: number) => {
    await taskApi.release({ task_id: taskId });
    await load();
  };

  const submitTask = async (releaseId: number) => {
    const answer = answers[releaseId]?.trim();
    if (!answer) return;
    await taskApi.submit(releaseId, answer);
    setAnswers((prev) => ({ ...prev, [releaseId]: "" }));
    setMessage("作业提交成功");
    await load();
  };

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div>
          <h1>作业中心</h1>
          <p>教师维护作业并发布，学生查看真实接口返回的作业并提交答案。</p>
        </div>
      </header>

      {message && <p className="course-empty">{message}</p>}

      {(role === "teacher" || role === "admin") && (
        <section className="course-card">
          <h2>作业题库</h2>
          <div className="course-form-grid">
            <input placeholder="课程ID" value={courseId} onChange={(e) => setCourseId(e.target.value)} />
            <input placeholder="作业内容" value={content} onChange={(e) => setContent(e.target.value)} />
            <button type="button" onClick={createTask}>创建作业</button>
          </div>
          {bank.map((item) => (
            <div className="course-list-item" key={item.task_id}>
              <div>
                <strong>课程 #{item.course_id}</strong>
                <p>{item.task_content}</p>
              </div>
              <button type="button" onClick={() => releaseTask(item.task_id)}>发布</button>
            </div>
          ))}
        </section>
      )}

      <section className="course-card">
        <h2>已发布作业</h2>
        {releases.length === 0 ? <p className="course-empty">暂无已发布作业</p> : null}
        {releases.map((item) => (
          <div className="course-list-item" key={item.task_publish_id}>
            <div>
              <strong>作业 #{item.task_publish_id}</strong>
              <p>{item.task_content ?? "无内容"}</p>
            </div>
            {role === "student" && (
              <div className="course-form-grid">
                <input placeholder="填写答案" value={answers[item.task_publish_id] ?? ""} onChange={(e) => setAnswers((prev) => ({ ...prev, [item.task_publish_id]: e.target.value }))} />
                <button type="button" onClick={() => submitTask(item.task_publish_id)}>提交</button>
              </div>
            )}
          </div>
        ))}
      </section>

      {role === "student" && (
        <section className="course-card">
          <h2>我的提交</h2>
          {submissions.map((item) => (
            <div className="course-list-item" key={item.submit_id}>
              <div>
                <strong>作业 #{item.task_publish_id}</strong>
                <p>得分：{item.score ?? "待批改"} · 评语：{item.comment ?? "暂无"}</p>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
