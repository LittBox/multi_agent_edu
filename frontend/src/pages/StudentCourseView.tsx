import { useEffect, useMemo } from "react";
import { ArrowRightLeft, RefreshCw } from "lucide-react";
import { useAcademicStore } from "../stores";
import "../styles/pages/CourseManagementView.css";

/** 学生选课页：上方公开课程，下方我的选课，小卡片复用通用毛玻璃卡片风格。 */
export default function StudentCourseView() {
  const {
    availableClasses = [],
    myEnrollments = [],
    loading,
    error,
    loadAvailableClasses,
    loadMyEnrollments,
    enrollClass,
    dropEnrollment,
  } = useAcademicStore();

  const refresh = async () => {
    await Promise.all([loadAvailableClasses(), loadMyEnrollments()]);
  };

  useEffect(() => {
    void refresh();
  }, []);

  const myClassIds = useMemo(
    () => new Set(myEnrollments.map((item) => item.class_id)),
    [myEnrollments]
  );

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

      {error && <p className="course-empty">{error}</p>}

      <section className="student-course-section">
        <h2>公开课程</h2>

        {loading && <p className="course-empty">加载中…</p>}
        {!loading && availableClasses.length === 0 && (
          <p className="course-empty">暂无公开课程</p>
        )}

        <div className="glass-card-grid">
          {availableClasses.map((item) => {
            const joined = myClassIds.has(item.class_id);

            return (
              <article
                className="course-item course-mini-card glass-mini-card"
                key={item.class_id}
              >
                <div>
                  <h3>{item.course_name || `课程 ${item.course_id}`}</h3>
                  <p>
                    {item.class_name} · {item.semester}
                  </p>
                  <span>{item.teacher_name || "任课教师未知"}</span>
                  <p>
                    容量：{item.current_count}/{item.capacity} · 第{" "}
                    {item.start_week}-{item.end_week} 周
                  </p>
                  <p>{item.location || "地点待定"}</p>
                </div>

                <div className="course-item-actions">
                  <button
                    disabled={joined}
                    type="button"
                    onClick={async () => {
                      await enrollClass(item.class_id);
                      await refresh();
                    }}
                  >
                    {joined ? "已选" : "加入课程"}
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="student-course-section">
        <h2>我已选择的课程</h2>

        {!loading && myEnrollments.length === 0 && (
          <p className="course-empty">暂无已选课程</p>
        )}

        <div className="glass-card-grid">
          {myEnrollments.map((item) => (
            <article
              className="course-item course-mini-card glass-mini-card"
              key={item.enrollment_id}
            >
              <div>
                <h3>{item.course_name}</h3>
                <p>
                  {item.class_name} · {item.semester}
                </p>
                <span>{item.teacher_name}</span>
                <p>
                  状态：{item.enroll_status} · 成绩：
                  {item.course_score ?? "暂无"}
                </p>
              </div>

              <div className="course-item-actions">
                <button
                  type="button"
                  onClick={async () => {
                    await dropEnrollment(item.enrollment_id);
                    await refresh();
                  }}
                >
                  <ArrowRightLeft size={16} />
                  退课
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}