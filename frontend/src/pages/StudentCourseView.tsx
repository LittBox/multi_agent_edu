import { useEffect, useMemo, useState } from "react";
import { ArrowRightLeft, RefreshCw } from "lucide-react";
import {
  dropEnrollment,
  enrollClass,
  listAvailableClasses,
  listMyEnrollments,
  type EnrolledClassInfo,
  type TeachingClassDetail,
} from "../api/academic";
import "../styles/pages/CourseManagementView.css";

interface StudentCourseViewProps {
  userId: number;
}

const StudentCourseView: React.FC<StudentCourseViewProps> = ({ userId }) => {
  const [availableClasses, setAvailableClasses] = useState<TeachingClassDetail[]>([]);
  const [enrollments, setEnrollments] = useState<EnrolledClassInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    setLoading(true);
    try {
      const [available, mine] = await Promise.all([
        listAvailableClasses(),
        listMyEnrollments(),
      ]);
      setAvailableClasses(available);
      setEnrollments(mine);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const myClassIds = useMemo(() => new Set(enrollments.map((item) => item.class_id)), [enrollments]);

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div>
          <h1>课程选课</h1>
          <p>学生可以浏览可选课程，选择加入或退课。</p>
        </div>
        <div className="course-header-actions">
          <button className="course-btn ghost" type="button" onClick={refresh}>
            <RefreshCw size={16} /> 刷新
          </button>
        </div>
      </header>

      <section className="course-card">
        <h2>我已选的课程</h2>
        {loading ? <p className="course-empty">加载中…</p> : enrollments.length === 0 ? <p className="course-empty">暂无已选课程</p> : (
          <div className="course-list">
            {enrollments.map((item) => (
              <article className="course-item" key={item.enrollment_id}>
                <div>
                  <h3>{item.course_name}</h3>
                  <p>{item.class_name} · {item.semester}</p>
                  <span>{item.teacher_name}</span>
                </div>
                <div className="course-item-actions">
                  <button type="button" onClick={async () => { await dropEnrollment(item.enrollment_id); await refresh(); }}>
                    <ArrowRightLeft size={16} /> 退课
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="course-card">
        <h2>可选课程</h2>
        {availableClasses.length === 0 ? <p className="course-empty">暂无可选课程</p> : (
          <div className="course-list">
            {availableClasses.map((item) => (
              <article className="course-item" key={item.class_id}>
                <div>
                  <h3>{item.course_name || `课程 ${item.course_id}`}</h3>
                  <p>{item.class_name} · {item.semester}</p>
                  <span>{item.teacher_name || "任课教师未知"}</span>
                </div>
                <div className="course-item-actions">
                  <button type="button" disabled={myClassIds.has(item.class_id)} onClick={async () => { await enrollClass(item.class_id); await refresh(); }}>
                    {myClassIds.has(item.class_id) ? "已选" : "加入课程"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default StudentCourseView;
