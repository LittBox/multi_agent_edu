import { useEffect, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { useAcademicStore } from "../stores";
import type { UserRole } from "../api/auth";
import "../styles/pages/CourseManagementView.css";

interface CourseManagementViewProps { role: UserRole; }

/** 教师/管理员课程管理页：课程和教学班上下分区，创建表单保留基础字段。 */
export default function CourseManagementView({ role }: CourseManagementViewProps) {
  const { courses, classes, loading, error, loadCourses, loadClasses, createCourse, createClass, deleteCourse } = useAcademicStore();
  const [courseCode, setCourseCode] = useState("");
  const [courseName, setCourseName] = useState("");
  const [credit, setCredit] = useState("3");
  const [description, setDescription] = useState("");
  const [classCourseId, setClassCourseId] = useState("");
  const [className, setClassName] = useState("");
  const [semester, setSemester] = useState("2026春季学期");
  const [capacity, setCapacity] = useState("60");

  const refresh = async () => { await Promise.all([loadCourses(), loadClasses()]); };
  useEffect(() => { void refresh(); }, []);

  const submitCourse = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!courseCode.trim() || !courseName.trim()) return;
    await createCourse({ course_code: courseCode.trim(), course_name: courseName.trim(), credit: Number(credit), description: description.trim() || null });
    setCourseCode(""); setCourseName(""); setDescription("");
  };

  const submitClass = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!classCourseId || !className.trim()) return;
    await createClass({
      course_id: Number(classCourseId),
      semester: semester.trim(),
      class_name: className.trim(),
      capacity: Number(capacity),
      start_week: 1,
      end_week: 16,
      location: null,
      schedules: [{ weekday: 1, start_time: "08:00", end_time: "09:40", week_start: 1, week_end: 16 }],
    });
    setClassCourseId(""); setClassName("");
  };

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div><h1>课程管理</h1><p>{role === "admin" ? "管理员可查看课程与教学班。" : "教师可创建课程、开设教学班。"}</p></div>
        <div className="course-header-actions"><button className="course-btn ghost" type="button" onClick={() => void refresh()}><RefreshCw size={16} />刷新</button></div>
      </header>

      <div className="course-stats">
        <div className="course-stat"><strong>{courses.length}</strong><span>课程数量</span></div>
        <div className="course-stat"><strong>{classes.length}</strong><span>教学班数量</span></div>
      </div>
      {loading && <p className="course-empty">加载中…</p>}
      {error && <p className="course-empty">{error}</p>}

      <section className="course-card">
        <h2>课程列表</h2>
        {role !== "student" && (
          <form className="course-form" onSubmit={submitCourse}>
            <label>课程代码<input value={courseCode} onChange={(e) => setCourseCode(e.target.value)} /></label>
            <label>课程名称<input value={courseName} onChange={(e) => setCourseName(e.target.value)} /></label>
            <label>学分<input value={credit} onChange={(e) => setCredit(e.target.value)} type="number" min="0.5" step="0.5" /></label>
            <label>课程描述<textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label>
            <button className="course-btn primary" type="submit"><Plus size={16} />创建课程</button>
          </form>
        )}
        <div className="course-list course-grid-list">
          {courses.map((course) => (
            <article className="course-item course-mini-card" key={course.course_id}>
              <div><h3>{course.course_name}</h3><p>{course.course_code} · {course.credit} 学分</p><span>{course.status}</span><p>{course.description || "暂无描述"}</p></div>
              <div className="course-item-actions"><button type="button" onClick={() => void deleteCourse(course.course_id)}>删除</button></div>
            </article>
          ))}
        </div>
      </section>

      <section className="course-card">
        <h2>教学班</h2>
        {role !== "student" && (
          <form className="course-form" onSubmit={submitClass}>
            <label>课程 ID<input value={classCourseId} onChange={(e) => setClassCourseId(e.target.value)} /></label>
            <label>教学班名称<input value={className} onChange={(e) => setClassName(e.target.value)} /></label>
            <label>学期<input value={semester} onChange={(e) => setSemester(e.target.value)} /></label>
            <label>容量<input value={capacity} onChange={(e) => setCapacity(e.target.value)} type="number" min="1" /></label>
            <button className="course-btn primary" type="submit"><Plus size={16} />创建教学班</button>
          </form>
        )}
        <div className="course-list course-grid-list">
          {classes.map((item) => (
            <article className="course-item course-mini-card" key={item.class_id}>
              <div><h3>{item.class_name}</h3><p>{item.semester} · {item.status}</p><span>课程 ID：{item.course_id}</span><p>人数：{item.current_count}/{item.capacity} · 第 {item.start_week}-{item.end_week} 周</p></div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
