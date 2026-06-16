import request from "./request";

/** =========================
 * 学生 / 教师基础档案
 * ========================= */
export interface StudentCreateParams {
  user_id: number;
  student_no: string;
  student_name: string;
  major?: string | null;
  grade?: number | null;
  class_name?: string | null;
}

export type StudentUpdateParams = Partial<Omit<StudentCreateParams, "user_id">>;

export interface Student {
  student_id: number;
  user_id: number;
  student_no: string;
  student_name: string;
  major?: string | null;
  grade?: number | null;
  class_name?: string | null;
  is_deleted?: number;
  created_at?: string;
  updated_at?: string;
}

export interface TeacherCreateParams {
  user_id: number;
  teacher_no: string;
  teacher_name: string;
  department?: string | null;
  title?: string | null;
}

export type TeacherUpdateParams = Partial<Omit<TeacherCreateParams, "user_id">>;

export interface Teacher {
  teacher_id: number;
  user_id: number;
  teacher_no: string;
  teacher_name: string;
  department?: string | null;
  title?: string | null;
  is_deleted?: number;
  created_at?: string;
  updated_at?: string;
}

/** =========================
 * 课程
 * ========================= */
export interface CourseCreateParams {
  course_code: string;
  course_name: string;
  credit: number;
  description?: string | null;
  /** 新后端由当前登录教师确定 teacher_id；保留可选字段兼容旧表单。 */
  teacher_id?: number;
}

export interface CourseUpdateParams {
  course_code?: string;
  course_name?: string;
  credit?: number;
  description?: string | null;
  status?: "draft" | "active" | "closed" | string;
}

export interface Course {
  course_id: number;
  course_code: string;
  course_name: string;
  credit: number;
  description: string | null;
  created_by_teacher_id: number;
  status: string;
  is_deleted?: number;
  created_at?: string;
  updated_at?: string;
}

/** =========================
 * 教学班 / 选课
 * ========================= */
export interface TeachingClassSchedule {
  weekday: number;
  start_time: string;
  end_time: string;
  week_start: number;
  week_end: number;
  classroom?: string | null;
  day?: number;
  time?: string;
}

export interface TeachingClassCreateParams {
  course_id: number;
  /** 新后端由当前登录教师确定 teacher_id；保留可选字段兼容旧表单。 */
  teacher_id?: number;
  semester: string;
  class_name: string;
  capacity: number;
  location?: string | null;
  start_week: number;
  end_week: number;
  schedules: TeachingClassSchedule[];
}

export interface TeachingClassUpdateParams {
  course_id?: number;
  teacher_id?: number;
  class_name?: string;
  capacity?: number;
  current_count?: number;
  status?: "open" | "closed" | "cancelled" | "finished" | string;
  semester?: string;
  location?: string | null;
  start_week?: number;
  end_week?: number;
  schedules?: TeachingClassSchedule[];
}

export interface TeachingClass {
  class_id: number;
  course_id: number;
  teacher_id: number;
  semester: string;
  class_name: string;
  capacity: number;
  current_count: number;
  status: string;
  location?: string | null;
  start_week: number;
  end_week: number;
  schedules?: TeachingClassSchedule[];
  is_deleted?: number;
  created_at?: string;
  updated_at?: string;
}

export interface TeachingClassDetail extends TeachingClass {
  course_name?: string | null;
  teacher_name?: string | null;
}

export interface Enrollment {
  enrollment_id: number;
  class_id: number;
  student_id: number;
  enroll_status: "enrolled" | "dropped" | string;
  enrolled_at: string;
  dropped_at: string | null;
  drop_reason?: string | null;
  course_score?: number | null;
  is_deleted?: number;
  created_at?: string;
  updated_at?: string;
}

export interface EnrolledClassInfo extends Enrollment {
  course_name: string;
  teacher_name: string;
  semester: string;
  class_name: string;
  schedules?: TeachingClassSchedule[];
}

export const academicApi = {
  /** 学生档案 */
  createStudent: (params: StudentCreateParams) => request.post<Student>("/academic/students", params),
  listStudents: () => request.get<Student[]>("/academic/students"),
  getStudent: (studentId: number) => request.get<Student>(`/academic/students/${studentId}`),
  getStudentByUser: (userId: number) => request.get<Student>(`/academic/students/by-user/${userId}`),
  updateStudent: (studentId: number, params: StudentUpdateParams) => request.patch<Student>(`/academic/students/${studentId}`, params),
  deleteStudent: (studentId: number) => request.delete<boolean>(`/academic/students/${studentId}`),

  /** 教师档案 */
  createTeacher: (params: TeacherCreateParams) => request.post<Teacher>("/academic/teachers", params),
  listTeachers: () => request.get<Teacher[]>("/academic/teachers"),
  getTeacher: (teacherId: number) => request.get<Teacher>(`/academic/teachers/${teacherId}`),
  getTeacherByUser: (userId: number) => request.get<Teacher>(`/academic/teachers/by-user/${userId}`),
  updateTeacher: (teacherId: number, params: TeacherUpdateParams) => request.patch<Teacher>(`/academic/teachers/${teacherId}`, params),
  deleteTeacher: (teacherId: number) => request.delete<boolean>(`/academic/teachers/${teacherId}`),

  /** 课程 */
  listCourses: () => request.get<Course[]>("/academic/courses"),
  getCourse: (courseId: number) => request.get<Course>(`/academic/courses/${courseId}`),
  createCourse: (params: CourseCreateParams) => request.post<Course>("/academic/courses", params),
  updateCourse: (courseId: number, params: CourseUpdateParams) => request.patch<Course>(`/academic/courses/${courseId}`, params),
  updateCourseStatus: (courseId: number, status: string) => request.patch<Course>(`/academic/courses/${courseId}/status`, null, { params: { status } }),
  deleteCourse: (courseId: number) => request.delete<boolean>(`/academic/courses/${courseId}`),
  listTeacherCourses: (teacherId: number) => request.get<Course[]>(`/academic/teachers/${teacherId}/courses`),

  /** 教学班 */
  listClasses: () => request.get<TeachingClass[]>("/academic/classes"),
  listOpenClasses: (semester?: string) => request.get<TeachingClassDetail[]>("/academic/classes/available", { params: semester ? { semester } : undefined }),
  getClassDetail: (classId: number) => request.get<TeachingClassDetail>(`/academic/classes/${classId}`),
  createClass: (params: TeachingClassCreateParams) => request.post<TeachingClassDetail>("/academic/classes", params),
  updateClass: (classId: number, params: TeachingClassUpdateParams) => request.patch<TeachingClass>(`/academic/classes/${classId}`, params),
  updateClassStatus: (classId: number, status: string) => request.patch<TeachingClass>(`/academic/classes/${classId}/status`, null, { params: { status } }),
  deleteClass: (classId: number) => request.delete<boolean>(`/academic/classes/${classId}`),
  listCourseClasses: (courseId: number) => request.get<TeachingClassDetail[]>(`/academic/courses/${courseId}/classes`),
  listTeacherClasses: (teacherId: number, semester?: string) => request.get<TeachingClass[]>(`/academic/teachers/${teacherId}/classes`, { params: semester ? { semester } : undefined }),
  listClassStudents: (classId: number) => request.get<Enrollment[]>(`/academic/classes/${classId}/students`),

  /** 选课 */
  enrollClass: (classId: number) => request.post<Enrollment>("/academic/enrollments", { class_id: classId }),
  dropEnrollment: (enrollmentId: number) => request.delete<boolean>(`/academic/enrollments/${enrollmentId}`),
  listMyEnrollments: (status = "enrolled") => request.get<EnrolledClassInfo[]>("/academic/enrollments/me", { params: { status } }),
  listAvailableClasses: (semester?: string) => request.get<TeachingClassDetail[]>("/academic/enrollments/available", { params: semester ? { semester } : undefined }),
  updateEnrollmentScore: (enrollmentId: number, courseScore: number | null) => request.patch<Enrollment>(`/academic/enrollments/${enrollmentId}/score`, null, { params: { course_score: courseScore } }),
};

/** 保留旧代码中的具名导出，避免页面组件大面积改 import。 */
export const listCourses = academicApi.listCourses;
export const getCourse = academicApi.getCourse;
export const createCourse = academicApi.createCourse;
export const updateCourse = academicApi.updateCourse;
export const updateCourseStatus = academicApi.updateCourseStatus;
export const deleteCourse = academicApi.deleteCourse;
export const listClasses = academicApi.listClasses;
export const getClassDetail = academicApi.getClassDetail;
export const createClass = academicApi.createClass;
export const updateClass = academicApi.updateClass;
export const closeClass =  (classId: number, _teacherId?: number): Promise<TeachingClass> =>
  academicApi.updateClassStatus(classId, "closed");
export const listClassStudents = academicApi.listClassStudents;
export const listClassSchedules = async (classId: number): Promise<TeachingClassSchedule[]> => {
  const detail = await academicApi.getClassDetail(classId);
  return detail.schedules ?? [];
};
export const listTeacherClasses = academicApi.listTeacherClasses;
export const enrollClass = academicApi.enrollClass;
export const dropEnrollment = academicApi.dropEnrollment;
export const listMyEnrollments = academicApi.listMyEnrollments;
export const listAvailableClasses = academicApi.listAvailableClasses;
