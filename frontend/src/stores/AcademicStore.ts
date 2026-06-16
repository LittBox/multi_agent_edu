import { create } from "zustand";
import {
  academicApi,
  type Course,
  type CourseCreateParams,
  type CourseUpdateParams,
  type EnrolledClassInfo,
  type Enrollment,
  type Student,
  type StudentCreateParams,
  type StudentUpdateParams,
  type Teacher,
  type TeacherCreateParams,
  type TeacherUpdateParams,
  type TeachingClass,
  type TeachingClassCreateParams,
  type TeachingClassDetail,
  type TeachingClassUpdateParams,
} from "../api/academic";

/**
 * 教务模块 Store。
 * 管理学生档案、教师档案、课程、教学班和学生选课数据。
 */
interface AcademicStore {
  students: Student[];
  teachers: Teacher[];
  courses: Course[];
  classes: TeachingClass[];
  availableClasses: TeachingClassDetail[];
  myEnrollments: EnrolledClassInfo[];
  selectedCourse: Course | null;
  selectedClass: TeachingClassDetail | null;
  loading: boolean;
  error: string | null;

  clearError: () => void;

  loadStudents: () => Promise<Student[]>;
  createStudent: (params: StudentCreateParams) => Promise<Student>;
  updateStudent: (studentId: number, params: StudentUpdateParams) => Promise<Student>;
  deleteStudent: (studentId: number) => Promise<void>;

  loadTeachers: () => Promise<Teacher[]>;
  createTeacher: (params: TeacherCreateParams) => Promise<Teacher>;
  updateTeacher: (teacherId: number, params: TeacherUpdateParams) => Promise<Teacher>;
  deleteTeacher: (teacherId: number) => Promise<void>;

  loadCourses: () => Promise<Course[]>;
  getCourse: (courseId: number) => Promise<Course>;
  createCourse: (params: CourseCreateParams) => Promise<Course>;
  updateCourse: (courseId: number, params: CourseUpdateParams) => Promise<Course>;
  deleteCourse: (courseId: number) => Promise<void>;

  loadClasses: () => Promise<TeachingClass[]>;
  getClassDetail: (classId: number) => Promise<TeachingClassDetail>;
  createClass: (params: TeachingClassCreateParams) => Promise<TeachingClassDetail>;
  updateClass: (classId: number, params: TeachingClassUpdateParams) => Promise<TeachingClass>;
  deleteClass: (classId: number) => Promise<void>;

  loadAvailableClasses: (semester?: string) => Promise<TeachingClassDetail[]>;
  loadMyEnrollments: (status?: string) => Promise<EnrolledClassInfo[]>;
  enrollClass: (classId: number) => Promise<Enrollment>;
  dropEnrollment: (enrollmentId: number) => Promise<void>;
  updateEnrollmentScore: (enrollmentId: number, courseScore: number | null) => Promise<Enrollment>;
}

function errorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

export const useAcademicStore = create<AcademicStore>((set, get) => ({
  students: [],
  teachers: [],
  courses: [],
  classes: [],
  availableClasses: [],
  myEnrollments: [],
  selectedCourse: null,
  selectedClass: null,
  loading: false,
  error: null,

  clearError: () => set({ error: null }),

  loadStudents: async () => {
    set({ loading: true, error: null });
    try {
      const students = await academicApi.listStudents();
      set({ students, loading: false });
      return students;
    } catch (error) {
      set({ loading: false, error: errorMessage(error, "加载学生列表失败") });
      throw error;
    }
  },

  createStudent: async (params) => {
    const student = await academicApi.createStudent(params);
    set((state) => ({ students: [student, ...state.students] }));
    return student;
  },

  updateStudent: async (studentId, params) => {
    const updated = await academicApi.updateStudent(studentId, params);
    set((state) => ({ students: state.students.map((item) => item.student_id === studentId ? updated : item) }));
    return updated;
  },

  deleteStudent: async (studentId) => {
    await academicApi.deleteStudent(studentId);
    set((state) => ({ students: state.students.filter((item) => item.student_id !== studentId) }));
  },

  loadTeachers: async () => {
    set({ loading: true, error: null });
    try {
      const teachers = await academicApi.listTeachers();
      set({ teachers, loading: false });
      return teachers;
    } catch (error) {
      set({ loading: false, error: errorMessage(error, "加载教师列表失败") });
      throw error;
    }
  },

  createTeacher: async (params) => {
    const teacher = await academicApi.createTeacher(params);
    set((state) => ({ teachers: [teacher, ...state.teachers] }));
    return teacher;
  },

  updateTeacher: async (teacherId, params) => {
    const updated = await academicApi.updateTeacher(teacherId, params);
    set((state) => ({ teachers: state.teachers.map((item) => item.teacher_id === teacherId ? updated : item) }));
    return updated;
  },

  deleteTeacher: async (teacherId) => {
    await academicApi.deleteTeacher(teacherId);
    set((state) => ({ teachers: state.teachers.filter((item) => item.teacher_id !== teacherId) }));
  },

  loadCourses: async () => {
    set({ loading: true, error: null });
    try {
      const courses = await academicApi.listCourses();
      set({ courses, loading: false });
      return courses;
    } catch (error) {
      set({ loading: false, error: errorMessage(error, "加载课程列表失败") });
      throw error;
    }
  },

  getCourse: async (courseId) => {
    const course = await academicApi.getCourse(courseId);
    set({ selectedCourse: course });
    return course;
  },

  createCourse: async (params) => {
    const course = await academicApi.createCourse(params);
    set((state) => ({ courses: [course, ...state.courses] }));
    return course;
  },

  updateCourse: async (courseId, params) => {
    const updated = await academicApi.updateCourse(courseId, params);
    set((state) => ({
      courses: state.courses.map((item) => item.course_id === courseId ? updated : item),
      selectedCourse: state.selectedCourse?.course_id === courseId ? updated : state.selectedCourse,
    }));
    return updated;
  },

  deleteCourse: async (courseId) => {
    await academicApi.deleteCourse(courseId);
    set((state) => ({ courses: state.courses.filter((item) => item.course_id !== courseId) }));
  },

  loadClasses: async () => {
    set({ loading: true, error: null });
    try {
      const classes = await academicApi.listClasses();
      set({ classes, loading: false });
      return classes;
    } catch (error) {
      set({ loading: false, error: errorMessage(error, "加载教学班列表失败") });
      throw error;
    }
  },

  getClassDetail: async (classId) => {
    const detail = await academicApi.getClassDetail(classId);
    set({ selectedClass: detail });
    return detail;
  },

  createClass: async (params) => {
    const detail = await academicApi.createClass(params);
    set((state) => ({ classes: [detail, ...state.classes], selectedClass: detail }));
    return detail;
  },

  updateClass: async (classId, params) => {
    const updated = await academicApi.updateClass(classId, params);
    set((state) => ({
      classes: state.classes.map((item) => item.class_id === classId ? updated : item),
      selectedClass: state.selectedClass?.class_id === classId ? { ...state.selectedClass, ...updated } : state.selectedClass,
    }));
    return updated;
  },

  deleteClass: async (classId) => {
    await academicApi.deleteClass(classId);
    set((state) => ({ classes: state.classes.filter((item) => item.class_id !== classId) }));
  },

  loadAvailableClasses: async (semester) => {
    set({ loading: true, error: null });
    try {
      const availableClasses = await academicApi.listAvailableClasses(semester);
      set({ availableClasses, loading: false });
      return availableClasses;
    } catch (error) {
      set({ loading: false, error: errorMessage(error, "加载可选课程失败") });
      throw error;
    }
  },

  loadMyEnrollments: async (status = "enrolled") => {
    set({ loading: true, error: null });
    try {
      const myEnrollments = await academicApi.listMyEnrollments(status);
      set({ myEnrollments, loading: false });
      return myEnrollments;
    } catch (error) {
      set({ loading: false, error: errorMessage(error, "加载我的选课失败") });
      throw error;
    }
  },

  enrollClass: async (classId) => {
    const enrollment = await academicApi.enrollClass(classId);
    await Promise.all([get().loadAvailableClasses(), get().loadMyEnrollments()]);
    return enrollment;
  },

  dropEnrollment: async (enrollmentId) => {
    await academicApi.dropEnrollment(enrollmentId);
    await Promise.all([get().loadAvailableClasses(), get().loadMyEnrollments()]);
  },

  updateEnrollmentScore: async (enrollmentId, courseScore) => {
    const updated = await academicApi.updateEnrollmentScore(enrollmentId, courseScore);
    set((state) => ({
      myEnrollments: state.myEnrollments.map((item) => item.enrollment_id === enrollmentId ? { ...item, course_score: updated.course_score } : item),
    }));
    return updated;
  },
}));
