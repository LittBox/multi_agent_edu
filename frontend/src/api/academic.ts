import request from "./request";

export interface CourseCreateParams {
  course_code: string;
  course_name: string;
  credit: number;
  description?: string | null;
  teacher_id: number;
}

export interface CourseUpdateParams {
  course_name?: string;
  credit?: number;
  description?: string | null;
  status?: string;
}

export interface Course {
  course_id: number;
  course_code: string;
  course_name: string;
  credit: number;
  description: string | null;
  created_by_teacher_id: number;
  status: string;
}

export interface TeachingClassSchedule {
  weekday: number;
  start_time: string;
  end_time: string;
  week_start: number;
  week_end: number;
  classroom?: string | null;
}

export interface TeachingClassCreateParams {
  course_id: number;
  teacher_id: number;
  semester: string;
  class_name: string;
  capacity: number;
  location?: string | null;
  start_week: number;
  end_week: number;
  schedules: TeachingClassSchedule[];
}

export interface TeachingClassUpdateParams {
  class_name?: string;
  capacity?: number;
  status?: string;
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
}

export interface TeachingClassDetail extends TeachingClass {
  course_name?: string | null;
  teacher_name?: string | null;
}

export interface Enrollment {
  enrollment_id: number;
  class_id: number;
  student_id: number;
  enroll_status: string;
  enrolled_at: string;
  dropped_at: string | null;
}

export interface EnrolledClassInfo extends Enrollment {
  course_name: string;
  teacher_name: string;
  semester: string;
  class_name: string;
  schedules: TeachingClassSchedule[];
}

export const listCourses = (): Promise<Course[]> =>
  request.get("/academic/courses");

export const getCourse = (courseId: number): Promise<Course> =>
  request.get(`/academic/courses/${courseId}`);

export const createCourse = (params: CourseCreateParams): Promise<Course> =>
  request.post("/academic/courses", params);

export const updateCourse = (
  courseId: number,
  params: CourseUpdateParams
): Promise<Course> => request.patch(`/academic/courses/${courseId}`, params);

export const updateCourseStatus = (
  courseId: number,
  status: string
): Promise<Course> =>
  request.patch(`/academic/courses/${courseId}/status`, null, {
    params: { status },
  });

export const deleteCourse = (courseId: number): Promise<null> =>
  request.delete(`/academic/courses/${courseId}`);

export const listClasses = (): Promise<TeachingClass[]> =>
  request.get("/academic/classes");

export const getClassDetail = (
  classId: number
): Promise<TeachingClassDetail> =>
  request.get(`/academic/classes/${classId}`);

export const createClass = (
  params: TeachingClassCreateParams
): Promise<TeachingClassDetail> =>
  request.post("/academic/classes", params);

export const updateClass = (
  classId: number,
  params: TeachingClassUpdateParams
): Promise<TeachingClass> =>
  request.patch(`/academic/classes/${classId}`, params);

export const closeClass = (
  classId: number,
  teacherId: number
): Promise<null> =>
  request.patch(`/academic/classes/${classId}/close`, null, {
    params: { teacher_id: teacherId },
  });

export const listClassStudents = (classId: number): Promise<Enrollment[]> =>
  request.get(`/academic/classes/${classId}/students`);

export const listClassSchedules = (
  classId: number
): Promise<TeachingClassSchedule[]> =>
  request.get(`/academic/classes/${classId}/schedules`);

export const listTeacherClasses = (
  teacherId: number,
  semester?: string
): Promise<TeachingClass[]> =>
  request.get(`/academic/teachers/${teacherId}/classes`, {
    params: semester ? { semester } : undefined,
  });

export const enrollClass = (classId: number): Promise<Enrollment> =>
  request.post("/academic/enrollments", { class_id: classId });

export const dropEnrollment = (enrollmentId: number): Promise<null> =>
  request.delete(`/academic/enrollments/${enrollmentId}`);

export const listMyEnrollments = (
  status = "enrolled"
): Promise<EnrolledClassInfo[]> =>
  request.get("/academic/enrollments/me", {
    params: { status },
  });

export const listAvailableClasses = (
  semester?: string
): Promise<TeachingClassDetail[]> =>
  request.get("/academic/enrollments/available", {
    params: semester ? { semester } : undefined,
  });