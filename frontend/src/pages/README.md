# pages_complete_latest

这套 pages/view 层文件用于对齐最新的后端 router、前端 api 请求层和 Zustand store 层。

## 放置位置

建议放到：

```text
src/pages/
```

并保持你的项目结构类似：

```text
src/api/
src/store/
src/pages/
src/styles/pages/
```

## 文件说明

- `LoginFormPage.tsx`：登录 / 注册页面，使用 `useAuthStore`。
- `DashboardPage.tsx`：主页面壳，负责侧边栏导航和视图切换。
- `CourseManagementView.tsx`：教师 / 管理员课程与教学班管理。
- `StudentCourseView.tsx`：学生选课页面，上方公开课程，下方已选课程。
- `KnowledgeWarehouseView.tsx`：知识仓库页面，检索、筛选、加入知识点和打开练习弹窗。
- `PracticePage.tsx`：练习弹窗。
- `ExamView.tsx`：考试列表、考试中、考试提交记录。
- `TaskView.tsx`：作业题库、已发布作业、我的提交。
- `ProfileView.tsx`：个人主页。
- `ReportView.tsx`：学习报告。
- `SettingsView.tsx`：资料和密码设置。
- `AdminView.tsx`：后台角色、菜单、权限管理。

## 样式说明

本次只调整逻辑和布局结构，未修改你已有样式文件。页面仍然引用：

```text
../styles/pages/DashboardPage.css
../styles/pages/CourseManagementView.css
../styles/pages/KnowledgeWarehousePage.css
../styles/pages/PracticePage.css
../styles/pages/ProfileView.css
../styles/pages/ReportView.css
../styles/pages/SettingsView.css
../styles/pages/LoginFormPage.css
```

后续你可以继续单独调整这些 CSS 文件。
