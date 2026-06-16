# store_complete_latest

这是一套与最新前端请求层和后端 router/service 对齐的 Zustand Store。

## 文件说明

- `AuthStore.ts`：登录、注册、退出、恢复登录态、刷新当前用户。
- `AcademicStore.ts`：学生、教师、课程、教学班、选课、课程成绩。
- `KnowledgeStore.ts`：知识仓库、知识点详情、加入知识点、知识点管理。
- `EducationStore.ts`：题库、下一题、提交答案、学习进度、复习计划、学习报告、智能助教。
- `ExamStore.ts`：考试列表、创建考试、组卷、进入考试、提交考试、考试记录、批阅。
- `TaskStore.ts`：作业题库、发布作业、提交作业、我的提交、批改。
- `DashboardStore.ts`：首页仪表盘、知识卡片。
- `AdminStore.ts`：后台统计、角色、菜单、权限、角色权限、权限菜单。
- `UserStore.ts`：个人主页、资料更新、修改密码。

## 使用方式

把这些文件放入前端项目的：

```text
src/store/
```

如果你的目录叫 `src/stores/`，也可以直接放入该目录。文件里的 API 引用是 `../api/...`，也就是默认 Store 与 API 目录同级：

```text
src/api/
src/store/
```

## 注意

1. 所有 Store 都保留 `loading / error`，页面可以直接读取展示加载状态和错误提示。
2. 写操作成功后会同步更新本地 state，减少页面重复刷新。
3. 对于选课、退课、提交作业、提交考试这类会影响多个列表的操作，Store 中已经做了必要的本地刷新或本地更新。
