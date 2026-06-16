# router_complete_latest

这是一套与最新 service 层配套的 FastAPI router 层代码。

## 包含文件

- `auth.py`：登录、注册、当前用户、修改密码、用户状态。
- `user.py`：个人中心、个人资料、密码修改。
- `academic.py`：学生、教师、课程、教学班、选课、退课、成绩。
- `knowledge.py`：知识点、知识仓库、加入知识点。
- `education.py`：题库、练习、提交答案、学习报告。
- `exams.py`：考试创建、组卷、进入考试、提交、成绩复核。
- `tasks.py`：作业题库、作业发布、作业提交、作业批改。
- `admin.py`：后台统计、角色、菜单、权限、关联关系。
- `dashboard.py`：学习仪表盘。
- `health.py`：健康检查。

## main.py 挂载示例

```python
from app.api import academic, admin, auth, dashboard, education, exams, health, knowledge, tasks, user

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(academic.router)
app.include_router(knowledge.router)
app.include_router(education.router)
app.include_router(exams.router)
app.include_router(tasks.router)
app.include_router(admin.router)
app.include_router(dashboard.router)
app.include_router(health.router)
```

## 前端重点接口

### 学生选课页

- `GET /academic/enrollments/available`
- `GET /academic/enrollments/me`
- `POST /academic/enrollments`
- `DELETE /academic/enrollments/{enrollment_id}`

### 考试页

- `GET /exams`
- `POST /exams`
- `GET /exams/{exam_id}/start`
- `POST /exams/{exam_id}/submit`
- `GET /exams/submissions/me`

### 作业页

- `GET /tasks/bank`
- `POST /tasks/bank`
- `POST /tasks/releases`
- `GET /tasks/releases`
- `POST /tasks/releases/{task_publish_id}/submit`
- `GET /tasks/submissions/me`

### 知识仓库页

- `GET /knowledge/repository/{user_id}`
- `POST /knowledge/{knowledge_id}/join?user_id=xxx`
- `GET /education/questions?user_id=xxx&knowledge_id=xxx`
