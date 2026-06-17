import { useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { useExamStore } from "../stores";
import { useRoleStore } from "../stores/RoleStore";
import type { UserRole } from "../api/auth";
import "../styles/pages/CourseManagementView.css";

interface ExamViewProps {
  role: UserRole;
}

/** 考试页：已发布考试、正在考试、我的提交记录上下分区。 */
export default function ExamView({ role }: ExamViewProps) {
  const {
    exams,
    currentExam,
    questions,
    answers,
    mySubmissions,
    loading,
    error,
    message,
    loadExams,
    createExam,
    startExam,
    setAnswer,
    submitExam,
    loadMySubmissions,
  } = useExamStore();

  const {
    studentInfo,
    getMyStudentInfo,
  } = useRoleStore();

  const [title, setTitle] = useState("");
  const [courseId, setCourseId] = useState("");

  const isStudent = role === "student";
  const canManageExams = role === "teacher" || role === "admin";

  const refresh = async () => {
    await loadExams();

    if (isStudent) {
      await Promise.all([
        loadMySubmissions(),
        getMyStudentInfo().catch(() => undefined),
      ]);
    }
  };

  useEffect(() => {
    void refresh();
  }, [role]);

  const visibleExams = useMemo(
    () =>
      isStudent
        ? exams.filter((item) =>
            ["published", "active", "ongoing"].includes(item.status)
          )
        : exams,
    [exams, isStudent]
  );

  const create = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!title.trim() || !courseId) return;

    await createExam({
      title: title.trim(),
      course_id: Number(courseId),
      duration_minutes: 60,
      exam_type: "quiz",
      status: "published",
    });

    setTitle("");
    setCourseId("");
  };

  const studentDisplayName =
    studentInfo?.student_name ||
    studentInfo?.username ||
    "未填写姓名";

  const studentDisplayId =
    studentInfo?.student_no ||
    studentInfo?.student_id ||
    studentInfo?.user_id;

  return (
    <div className="course-management-view">
      <header className="course-header">

        <div className="course-header-actions">
          <button
            className="course-btn ghost"
            type="button"
            onClick={() => void refresh()}
          >
            <RefreshCw size={16} />
            刷新
          </button>
        </div>
      </header>

      {message && <p className="course-empty">{message}</p>}
      {error && <p className="course-empty">{error}</p>}

      {canManageExams && (
        <section className="student-course-section exam-section">
          <h2>创建考试</h2>

          <div className="glass-card-grid">
            <form
              className="course-form exam-create-card glass-mini-card"
              onSubmit={create}
            >
              <h3>创建并发布考试</h3>

              <label>
                考试标题
                <input
                  value={title}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="请输入考试标题"
                />
              </label>

              <label>
                课程 ID
                <input
                  value={courseId}
                  onChange={(event) => setCourseId(event.target.value)}
                  placeholder="请输入课程 ID"
                />
              </label>

              <button className="course-btn primary" type="submit">
                <Plus size={16} />
                创建并发布
              </button>
            </form>
          </div>
        </section>
      )}

      <section className="student-course-section exam-section">
        <h2>{isStudent ? "已发布考试" : "考试列表"}</h2>

        {loading && <p className="course-empty">加载中…</p>}

        {!loading && visibleExams.length === 0 && (
          <p className="course-empty">暂无考试</p>
        )}

        <div className="glass-card-grid">
          {visibleExams.map((exam) => (
            <article
              className="course-item course-mini-card glass-mini-card"
              key={exam.exam_id}
            >
              <div>
                <h3>{exam.title || "未命名考试"}</h3>
                <p>
                  课程 ID：{exam.course_id} · {exam.duration_minutes} 分钟
                </p>
                <span>
                  {exam.exam_type} · {exam.status}
                </span>
              </div>

              {isStudent && (
                <div className="course-item-actions">
                  <button
                    type="button"
                    onClick={() => void startExam(exam.exam_id)}
                  >
                    进入考试
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      </section>

      {isStudent && (
        <section className="student-course-section exam-section">
          <h2>正在进行中的考试</h2>

          {!currentExam && (
            <p className="course-empty">点击上方考试卡片开始答题。</p>
          )}

          {currentExam && (
            <>
              <div className="glass-card-grid">
                <article className="course-item course-mini-card glass-mini-card exam-current-card">
                  <div>
                    <h3>{currentExam.title || "未命名考试"}</h3>
                    <p>考试时长：{currentExam.duration_minutes} 分钟</p>
                    <span>请完成下方题目后提交试卷。</span>
                  </div>
                </article>
              </div>

              {questions.length === 0 && (
                <p className="course-empty">当前试卷暂无题目。</p>
              )}

              <div className="glass-card-grid">
                {questions.map((question, index) => (
                  <article
                    className="course-item course-mini-card glass-mini-card exam-question-card"
                    key={question.exam_question_id}
                  >
                    <div>
                      <h3>
                        {index + 1}. {question.stem}
                      </h3>

                      <div className="exam-option-list">
                        <p>A. {question.option_a ?? "-"}</p>
                        <p>B. {question.option_b ?? "-"}</p>
                        <p>C. {question.option_c ?? "-"}</p>
                        <p>D. {question.option_d ?? "-"}</p>
                      </div>

                      <input
                        className="exam-answer-input"
                        value={answers[String(question.question_id)] ?? ""}
                        onChange={(event) =>
                          setAnswer(question.question_id, event.target.value)
                        }
                        placeholder="请输入答案"
                      />
                    </div>
                  </article>
                ))}
              </div>

              <div className="exam-submit-row">
                <button
                  className="course-btn primary"
                  type="button"
                  onClick={() => void submitExam(currentExam.exam_id)}
                >
                  提交试卷
                </button>
              </div>
            </>
          )}
        </section>
      )}

      {isStudent && (
        <section className="student-course-section exam-section">
          <h2>我的考试记录</h2>

          {!loading && mySubmissions.length === 0 && (
            <p className="course-empty">暂无考试提交记录</p>
          )}

          <div className="glass-card-grid">
            {mySubmissions.map((item) => {
              const submitRecord = item as typeof item & {
                exam_title?: string;
                title?: string;
                submitted_at?: string;
                submit_time?: string;
                created_at?: string;
              };

              const matchedExam = exams.find(
                (exam) => exam.exam_id === item.exam_id
              );

              const examTitle =
                matchedExam?.title ||
                submitRecord.exam_title ||
                submitRecord.title ||
                "未命名考试";

              const submitTime =
                submitRecord.submitted_at ||
                submitRecord.submit_time ||
                submitRecord.created_at;

              return (
                <article
                  className="course-item course-mini-card glass-mini-card"
                  key={item.exam_submit_id}
                >
                  <div>
                    <h3>{examTitle}</h3>

                    <p>
                      答卷人：{studentDisplayName}
                      {studentDisplayId ? ` · 学号/ID：${studentDisplayId}` : ""}
                    </p>

                    {submitTime && (
                      <p>提交时间：{new Date(submitTime).toLocaleString()}</p>
                    )}

                    <span>得分：{item.total_score ?? "待评分"}</span>
                    <p>评语：{item.teacher_comment || "暂无评语"}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}