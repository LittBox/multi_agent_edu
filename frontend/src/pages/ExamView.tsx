import { useEffect, useState } from "react";
import { examApi, type ExamDetail, type ExamItem, type ExamSubmissionItem } from "../api/exams";
import "../styles/pages/CourseManagementView.css";

interface ExamViewProps {
  role: "admin" | "teacher" | "student";
}

export default function ExamView({ role }: ExamViewProps) {
  const [exams, setExams] = useState<ExamItem[]>([]);
  const [current, setCurrent] = useState<ExamDetail | null>(null);
  const [submissions, setSubmissions] = useState<ExamSubmissionItem[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [title, setTitle] = useState("");
  const [courseId, setCourseId] = useState("");
  const [message, setMessage] = useState("");

  const load = async () => {
    try {
      setExams(await examApi.list());
      if (role === "student") {
        setSubmissions(await examApi.mySubmissions());
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "加载失败");
    }
  };

  useEffect(() => {
    void load();
  }, [role]);

  const createExam = async () => {
    if (!title.trim() || !courseId) return;
    await examApi.create({ title: title.trim(), course_id: Number(courseId), duration_minutes: 60, exam_type: "quiz", status: "published" });
    setTitle("");
    setCourseId("");
    await load();
  };

  const startExam = async (examId: number) => {
    setCurrent(await examApi.start(examId));
    setAnswers({});
  };

  const submitExam = async () => {
    if (!current) return;
    const result = await examApi.submit(current.exam_id, answers);
    setMessage(`提交成功，客观题得分：${result.total_score ?? 0}`);
    setCurrent(null);
    await load();
  };

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div>
          <h1>考试中心</h1>
          <p>教师创建考试和组卷，学生进入考试后完成答题提交，系统自动计算客观题分数。</p>
        </div>
      </header>

      {message && <p className="course-empty">{message}</p>}

      {(role === "teacher" || role === "admin") && (
        <section className="course-card">
          <h2>创建考试</h2>
          <div className="course-form-grid">
            <input placeholder="考试标题" value={title} onChange={(e) => setTitle(e.target.value)} />
            <input placeholder="课程ID" value={courseId} onChange={(e) => setCourseId(e.target.value)} />
            <button type="button" onClick={createExam}>创建并发布</button>
          </div>
          <p className="course-empty">组卷接口已提供：POST /api/v1/exams/{'{exam_id}'}/questions，可在题库页面继续接入选择题目。</p>
        </section>
      )}

      {current ? (
        <section className="course-card">
          <h2>{current.title}</h2>
          <p>考试时长：{current.duration_minutes} 分钟</p>
          {current.questions.length === 0 ? <p className="course-empty">当前试卷暂无题目，请联系教师组卷。</p> : null}
          {current.questions.map((q, index) => (
            <div className="course-list-item" key={q.exam_question_id}>
              <div>
                <strong>{index + 1}. {q.stem}</strong>
                <p>A. {q.option_a ?? "-"}</p>
                <p>B. {q.option_b ?? "-"}</p>
                <p>C. {q.option_c ?? "-"}</p>
                <p>D. {q.option_d ?? "-"}</p>
                <input placeholder="答案" value={answers[String(q.question_id)] ?? ""} onChange={(e) => setAnswers((prev) => ({ ...prev, [String(q.question_id)]: e.target.value }))} />
              </div>
            </div>
          ))}
          <button type="button" onClick={submitExam}>提交试卷</button>
        </section>
      ) : (
        <section className="course-card">
          <h2>考试列表</h2>
          {exams.length === 0 ? <p className="course-empty">暂无考试</p> : null}
          {exams.map((item) => (
            <div className="course-list-item" key={item.exam_id}>
              <div>
                <strong>{item.title}</strong>
                <p>课程 {item.course_id} · {item.exam_type} · {item.duration_minutes} 分钟 · {item.status}</p>
              </div>
              {role === "student" ? <button type="button" onClick={() => startExam(item.exam_id)}>进入考试</button> : null}
            </div>
          ))}
        </section>
      )}

      {role === "student" && (
        <section className="course-card">
          <h2>我的成绩</h2>
          {submissions.length === 0 ? <p className="course-empty">暂无考试提交</p> : null}
          {submissions.map((item) => (
            <div className="course-list-item" key={item.exam_submit_id}>
              <div>
                <strong>考试 #{item.exam_id}</strong>
                <p>得分：{item.total_score ?? "待评分"} · 评语：{item.teacher_comment ?? "暂无"}</p>
              </div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
