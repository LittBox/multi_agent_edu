import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Plus,
  Pencil,
  Trash2,
  RefreshCw,
  Users,
} from "lucide-react";
import {
  createCourse,
  deleteCourse,
  listCourses,
  updateCourse,
  createClass,
  closeClass,
  listTeacherClasses,
  type Course,
  type TeachingClass,
} from "../api/academic";
import "../styles/pages/CourseManagementView.css";

interface CourseManagementViewProps {
  userId: number;
}

const emptyCourseForm = {
  course_code: "",
  course_name: "",
  credit: 0,
  description: "",
  teacher_id: 0,
};

const emptyClassForm = {
  course_id: 0,
  class_name: "",
  semester: "",
  capacity: 50,
  weekday: 1,
  start_time: "08:00",
  end_time: "09:40",
  start_week: 1,
  end_week: 16,
  classroom: "",
  teacher_id: 0,
};

const CourseManagementView: React.FC<CourseManagementViewProps> = ({
  userId,
}) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [classes, setClasses] = useState<TeachingClass[]>([]);

  const [loading, setLoading] = useState(true);
  const [savingCourse, setSavingCourse] = useState(false);
  const [savingClass, setSavingClass] = useState(false);

  const [editing, setEditing] = useState<Course | null>(null);
  const [courseForm, setCourseForm] = useState(emptyCourseForm);
  const [classForm, setClassForm] = useState({
    ...emptyClassForm,
    teacher_id: userId,
  });

  const refresh = async () => {
    setLoading(true);

    try {
      const [courseData, classData] = await Promise.all([
        listCourses(),
        listTeacherClasses(userId),
      ]);

      setCourses(courseData);
      setClasses(classData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, [userId]);

  const stats = useMemo(
    () => ({
      total: courses.length,
      active: courses.filter((course) => course.status === "active").length,
      classTotal: classes.length,
      classActive: classes.filter((item) => item.status === "active").length,
    }),
    [courses, classes]
  );

  const getCourseName = (courseId: number) => {
    return (
      courses.find((course) => course.course_id === courseId)?.course_name ||
      `课程 ${courseId}`
    );
  };

  const startCreateCourse = () => {
    setEditing(null);
    setCourseForm({ ...emptyCourseForm, teacher_id: userId });
  };

  const startEditCourse = (course: Course) => {
    setEditing(course);
    setCourseForm({
      course_code: course.course_code,
      course_name: course.course_name,
      credit: course.credit,
      description: course.description ?? "",
      teacher_id: course.created_by_teacher_id,
    });
  };

  const startCreateClass = (course?: Course) => {
    setClassForm({
      ...emptyClassForm,
      course_id: course?.course_id ?? courses[0]?.course_id ?? 0,
      teacher_id: userId,
    });
  };

  const submitCourse = async () => {
    setSavingCourse(true);

    try {
      if (editing) {
        await updateCourse(editing.course_id, {
          course_name: courseForm.course_name,
          credit: courseForm.credit,
          description: courseForm.description || null,
        });
      } else {
        await createCourse({
          course_code: courseForm.course_code,
          course_name: courseForm.course_name,
          credit: courseForm.credit,
          description: courseForm.description || null,
          teacher_id: courseForm.teacher_id || userId,
        });
      }

      await refresh();
      startCreateCourse();
    } finally {
      setSavingCourse(false);
    }
  };

  const submitClass = async () => {
    if (!classForm.course_id) {
      alert("请先选择课程");
      return;
    }

    if (!classForm.class_name.trim()) {
      alert("请输入教学班名称");
      return;
    }

    if (!classForm.semester.trim()) {
      alert("请输入学期");
      return;
    }

    if (!classForm.capacity || classForm.capacity <= 0) {
      alert("请输入正确的容量");
      return;
    }

    if (!classForm.start_week || classForm.start_week <= 0) {
      alert("请输入正确的开始周");
      return;
    }

    if (!classForm.end_week || classForm.end_week < classForm.start_week) {
      alert("结束周不能小于开始周");
      return;
    }

    if (!classForm.start_time.trim()) {
      alert("请输入开始时间");
      return;
    }

    if (!classForm.end_time.trim()) {
      alert("请输入结束时间");
      return;
    }

    setSavingClass(true);

    try {
      await createClass({
        course_id: classForm.course_id,
        teacher_id: classForm.teacher_id || userId,
        semester: classForm.semester,
        class_name: classForm.class_name,
        capacity: classForm.capacity,
        location: classForm.classroom || null,
        start_week: classForm.start_week,
        end_week: classForm.end_week,
        schedules: [
          {
            weekday: classForm.weekday,
            start_time: classForm.start_time,
            end_time: classForm.end_time,
            week_start: classForm.start_week,
            week_end: classForm.end_week,
            classroom: classForm.classroom || null,
          },
        ],
      });

      await refresh();

      setClassForm({
        ...emptyClassForm,
        course_id: classForm.course_id,
        teacher_id: userId,
      });
    } finally {
      setSavingClass(false);
    }
  };

  const removeCourse = async (courseId: number) => {
    await deleteCourse(courseId);
    await refresh();
  };

  const handleCloseClass = async (classId: number) => {
    await closeClass(classId, userId);
    await refresh();
  };

  return (
    <div className="course-management-view">
      <header className="course-header">
        <div>
          <h1>课程管理</h1>
          <p>在这里维护课程和教学班。学生只能看到已经开设的教学班。</p>
        </div>

        <div className="course-header-actions">
          <button className="course-btn ghost" type="button" onClick={refresh}>
            <RefreshCw size={16} /> 刷新
          </button>

          <button
            className="course-btn primary"
            type="button"
            onClick={startCreateCourse}
          >
            <Plus size={16} /> 新建课程
          </button>

          <button
            className="course-btn primary"
            type="button"
            onClick={() => startCreateClass()}
          >
            <Users size={16} /> 新建教学班
          </button>
        </div>
      </header>

      <section className="course-stats">
        <div className="course-stat">
          <strong>{stats.total}</strong>
          <span>课程总数</span>
        </div>

        <div className="course-stat">
          <strong>{stats.active}</strong>
          <span>启用课程</span>
        </div>

        <div className="course-stat">
          <strong>{stats.classTotal}</strong>
          <span>教学班总数</span>
        </div>

        <div className="course-stat">
          <strong>{stats.classActive}</strong>
          <span>开放教学班</span>
        </div>
      </section>

      <section className="course-card course-form-card">
        <h2>
          <BookOpen size={18} />
          {editing ? "编辑课程" : "新建课程"}
        </h2>

        <div className="course-form">
          {!editing && (
            <label>
              课程编号
              <input
                value={courseForm.course_code}
                onChange={(e) =>
                  setCourseForm({
                    ...courseForm,
                    course_code: e.target.value,
                  })
                }
              />
            </label>
          )}

          <label>
            课程名称
            <input
              value={courseForm.course_name}
              onChange={(e) =>
                setCourseForm({
                  ...courseForm,
                  course_name: e.target.value,
                })
              }
            />
          </label>

          <label>
            学分
            <input
              type="number"
              value={courseForm.credit}
              onChange={(e) =>
                setCourseForm({
                  ...courseForm,
                  credit: Number(e.target.value),
                })
              }
            />
          </label>

          <label>
            课程简介
            <textarea
              value={courseForm.description}
              onChange={(e) =>
                setCourseForm({
                  ...courseForm,
                  description: e.target.value,
                })
              }
            />
          </label>

          <button
            className="course-btn primary"
            type="button"
            onClick={submitCourse}
            disabled={savingCourse}
          >
            {savingCourse ? "保存中…" : editing ? "保存修改" : "创建课程"}
          </button>
        </div>
      </section>

      <section className="course-card course-form-card">
        <h2>
          <Users size={18} />
          新建教学班
        </h2>

        <div className="course-form">
          <label>
            所属课程
            <select
              value={classForm.course_id}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  course_id: Number(e.target.value),
                })
              }
            >
              <option value={0}>请选择课程</option>
              {courses.map((course) => (
                <option key={course.course_id} value={course.course_id}>
                  {course.course_name}
                </option>
              ))}
            </select>
          </label>

          <label>
            教学班名称
            <input
              placeholder="例如：Python 2026 春季 1 班"
              value={classForm.class_name}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  class_name: e.target.value,
                })
              }
            />
          </label>

          <label>
            学期
            <input
              placeholder="例如：2026 Spring"
              value={classForm.semester}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  semester: e.target.value,
                })
              }
            />
          </label>

          <label>
            容量
            <input
              type="number"
              value={classForm.capacity}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  capacity: Number(e.target.value),
                })
              }
            />
          </label>

          <label>
            上课星期
            <select
              value={classForm.weekday}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  weekday: Number(e.target.value),
                })
              }
            >
              <option value={1}>周一</option>
              <option value={2}>周二</option>
              <option value={3}>周三</option>
              <option value={4}>周四</option>
              <option value={5}>周五</option>
              <option value={6}>周六</option>
              <option value={7}>周日</option>
            </select>
          </label>

          <label>
            开始时间
            <input
              type="time"
              value={classForm.start_time}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  start_time: e.target.value,
                })
              }
            />
          </label>

          <label>
            结束时间
            <input
              type="time"
              value={classForm.end_time}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  end_time: e.target.value,
                })
              }
            />
          </label>

          <label>
            开始周
            <input
              type="number"
              value={classForm.start_week}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  start_week: Number(e.target.value),
                })
              }
            />
          </label>

          <label>
            结束周
            <input
              type="number"
              value={classForm.end_week}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  end_week: Number(e.target.value),
                })
              }
            />
          </label>

          <label>
            教室
            <input
              placeholder="例如：A101"
              value={classForm.classroom}
              onChange={(e) =>
                setClassForm({
                  ...classForm,
                  classroom: e.target.value,
                })
              }
            />
          </label>

          <button
            className="course-btn primary"
            type="button"
            onClick={submitClass}
            disabled={savingClass || courses.length === 0}
          >
            {savingClass ? "创建中…" : "创建教学班"}
          </button>
        </div>
      </section>

      <section className="course-card">
        <h2>课程列表</h2>

        {loading ? (
          <p className="course-empty">加载中…</p>
        ) : courses.length === 0 ? (
          <p className="course-empty">暂无课程</p>
        ) : (
          <div className="course-list">
            {courses.map((course) => (
              <article className="course-item" key={course.course_id}>
                <div>
                  <h3>{course.course_name}</h3>
                  <p>
                    {course.course_code} · {course.credit} 学分
                  </p>
                  <span>{course.description || "暂无描述"}</span>
                </div>

                <div className="course-item-actions">
                  <button type="button" onClick={() => startEditCourse(course)}>
                    <Pencil size={16} /> 编辑
                  </button>

                  <button
                    type="button"
                    onClick={() => startCreateClass(course)}
                  >
                    <Users size={16} /> 开教学班
                  </button>

                  <button
                    type="button"
                    onClick={() => removeCourse(course.course_id)}
                  >
                    <Trash2 size={16} /> 关闭课程
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="course-card">
        <h2>教学班列表</h2>

        {loading ? (
          <p className="course-empty">加载中…</p>
        ) : classes.length === 0 ? (
          <p className="course-empty">暂无教学班，请先创建教学班</p>
        ) : (
          <div className="course-list">
            {classes.map((item) => (
              <article className="course-item" key={item.class_id}>
                <div>
                  <h3>{item.class_name}</h3>
                  <p>
                    {getCourseName(item.course_id)} · {item.semester}
                  </p>
                  <span>
                    容量 {item.capacity} · 已选 {item.enrolled_count} ·{" "}
                    {item.status === "active" ? "开放中" : item.status}
                  </span>
                </div>

                <div className="course-item-actions">
                  <button
                    type="button"
                    onClick={() => handleCloseClass(item.class_id)}
                  >
                    <Trash2 size={16} /> 关闭教学班
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

export default CourseManagementView;