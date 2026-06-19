# Edu Loop

## 1. 项目介绍

Edu Loop 是一个面向学生端学习练习场景的智能教育系统 Demo。当前阶段重点完成学生端知识点练习、答案提交、学习反馈和 AI 答题解析闭环。

当前项目已经完成学生端前后端基础联调，前端通过 HTTP 请求调用后端接口。WebSocket / 全双工通信能力后续再完善；教师端和管理员端完整界面暂不作为当前阶段重点。

当前主要链路如下：

```text
学生进入知识点练习
选择题目
选择答案
提交答案
后端处理答题结果
后端调用大模型生成答题解析
前端展示答题反馈与 AI 解析
```

## 2. 快速启动

### 2.1 后端启动

进入后端目录：

```bash
cd python
```

创建虚拟环境：

```bash
python -m venv .venv
```

激活虚拟环境：

```bash
source .venv/bin/activate
```

Windows 环境可使用：

```bash
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动后端服务：

```bash
uvicorn app.main:app --reload --port 8000
python -m app.main
```

后端启动后，可以访问接口文档：

```text
http://localhost:8000/docs
```

### 2.2 前端启动

进入前端目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

启动开发服务：

```bash
npm run dev
```

前端启动后，浏览器访问 Vite 终端输出的本地地址：

```text
http://localhost:3000
```

如果本地配置使用其他端口，以终端实际输出为准。

## 3. 环境变量配置

### 3.1 后端环境变量

后端 `.env` 放在：

```text
python/.env
```

示例：

```env
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat

DATABASE_URL=
REDIS_URL=

API_PORT=8000
LOG_LEVEL=INFO
DEBUG=True
```

说明：

- 后端 `.env` 用于保存模型 API Key、数据库地址、Redis 地址等服务端配置。
- 真实 `.env` 不应提交到 Git。
- 建议提交 `.env.example` 作为配置模板。
- 模型 API Key 只应放在后端，不应放在前端。

### 3.2 前端环境变量

前端 `.env` 放在：

```text
frontend/.env
```

示例：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

说明：

- 前端 `.env` 只保存前端需要访问的后端 API 地址。
- 不要在前端 `.env` 中保存 DeepSeek、OpenAI、MiniMax 等模型密钥。
- 前端环境变量会暴露到浏览器端，密钥必须只放在后端。

## 4. 当前开发状态

### 4.1 已完成

- 学生端基础页面与后端接口联调
- 知识点练习页题目展示
- 选项选择与答案提交
- 答题结果反馈
- AI 答题解析接口
- 前端展示 AI 返回的 Markdown 解析内容
- 后端 `.env` 读取模型 API Key
- 前端 `.env` 配置后端 API 地址
- 当前前后端通过 HTTP 通信

### 4.2 待完成

- 学生端交互和样式继续优化
- WebSocket / 全双工通信链路
- 实时 Agent 消息推送
- 教师端完整界面
- 管理员端完整界面
- 多角色完整业务闭环

## 5. 当前核心功能

### 5.1 学生端练习闭环

当前学生端已实现基础练习流程：

```text
进入知识点练习
选择题目
选择答案
提交答案
后端判断结果
更新学习数据
返回答题反馈
前端展示结果
```

### 5.2 AI 答题解析

当前学生答题后，前端会整理题目、学生答案、正确答案和知识点信息，请求后端生成 AI 答题解析。

流程如下：

```text
学生提交答案
前端整理题目、学生答案、正确答案、知识点
请求后端 /api/tutor/answer-analysis
后端调用 DeepSeek
返回 analysis
前端以 Markdown 形式展示解析
```

接口路径：

```text
POST /api/tutor/answer-analysis
```

## 6. 核心算法与学习变量

项目中的学习数据主要围绕 BKT、SM-2 和用户画像维度展开。BKT 用于判断学生当前是否掌握某个知识点，SM-2 用于判断知识点什么时候应该复习，用户画像维度用于在前端展示学生整体学习状态。

### 6.1 BKT：知识掌握度追踪

BKT 用来回答：

```text
学生现在会不会某个知识点
```

核心变量：

| 变量 | 含义 |
|---|---|
| `mastery` | 当前知识点掌握概率，取值范围为 0 到 1 |
| `attempts` | 当前知识点累计尝试次数 |
| `correct_attempts` | 当前知识点累计答对次数 |
| `streak` | 当前知识点连续答对次数 |
| `confidence` | 系统对 `mastery` 判断的确信程度 |
| `status` | 当前知识点学习状态，例如 learning、mastered |

说明：

- 正确率不等于掌握度。
- 正确率反映历史答题表现。
- `mastery` 是模型对学生真实掌握状态的估计。
- `confidence` 表示系统对当前 `mastery` 判断有多确信。

### 6.2 SM-2：间隔重复复习排期

SM-2 用来回答：

```text
这个知识点什么时候该复习
```

核心变量：

| 变量 | 含义 |
|---|---|
| `ef` / `easiness_factor` | 难度因子，表示该知识点对当前学生来说有多容易记住 |
| `quality` | 本次回答质量，通常取值范围为 0 到 5 |
| `interval_days` | 距离下次复习的间隔天数 |
| `repetition` | 连续成功复习次数 |
| `next_review_at` | 下次复习时间 |
| `last_review_at` | 上次复习时间 |
| `is_due` | 当前是否已经到复习时间 |
| `overdue_days` | 复习逾期天数 |

说明：

- BKT 负责判断学生当前会不会。
- SM-2 负责安排什么时候再复习。
- 两者分别处理学习状态判断和复习节奏安排。

### 6.3 用户画像五维度

用户画像用于前端展示学生整体学习状态。维度分数一般被限制在 0 到 100。

| 维度 | key | 含义 |
|---|---|---|
| 知识掌握 | `mastery` | 所有已跟踪知识点的平均掌握度 |
| 答题准确 | `accuracy` | 历史答题正确率 |
| 练习活跃 | `activity` | 最近 7 天练习量 |
| 学习稳定 | `consistency` | 最近 7 天持续学习情况 |
| 复习健康 | `review` | 是否按时复习 |

## 7. 当前核心接口

### 7.1 AI 答题解析接口

请求路径：

```text
POST /api/tutor/answer-analysis
```

请求示例：

```json
{
  "learner_id": "21",
  "knowledge_id": "106",
  "question": "谓词逻辑常用于人工智能中的哪一类任务？",
  "user_answer": "图像压缩",
  "correct_answer": "知识表示",
  "is_correct": false
}
```

响应示例：

```json
{
  "code": 0,
  "message": "OK",
  "data": {
    "learner_id": "21",
    "knowledge_id": "106",
    "is_correct": false,
    "agent": "TutorAgent",
    "model": "deepseek-chat",
    "analysis": "### 结论\n..."
  }
}
```

前端统一请求封装会自动取出响应中的 `data`，页面侧直接使用 `analysis` 字段进行展示。

## 8. 技术栈

| 技术栈名称 | 作用 |
|---|---|
| Python 3.11+ | 后端主要开发语言，支持异步编程能力 |
| FastAPI | 后端 HTTP API 框架 |
| Uvicorn | ASGI 服务运行器，用于启动 FastAPI 应用 |
| Pydantic v2 | 数据校验与配置管理 |
| SQLAlchemy | 数据库 ORM |
| Alembic | 数据库迁移管理 |
| asyncpg | PostgreSQL 异步数据库驱动 |
| Redis | 缓存与后续实时通信支持 |
| OpenAI SDK | 以兼容方式调用 DeepSeek API，生成答题解析 |
| python-dotenv / pydantic-settings | 读取和管理后端环境变量 |
| React | 前端页面开发框架 |
| TypeScript | 前端类型约束 |
| Vite | 前端构建与开发服务工具 |
| Zustand | 前端状态管理 |
| Axios | 前端 HTTP 请求封装 |
| React Router | 前端路由管理 |
| ECharts | 学习数据图表展示 |
| MUI | 前端 UI 组件支持 |
| Tailwind CSS | 前端样式开发支持 |

## 9. 项目结构

项目采用前后端分离结构。以下目录已去掉 `__pycache__` 等运行缓存目录。

### 9.1 前端结构

```text
frontend/
└── src/
    ├── api/                    # 前端接口请求封装
    ├── components/             # 通用组件
    │   ├── AuthCarousel/
    │   ├── DashboardLayout/
    │   ├── GhostMouse/
    │   ├── GlassToast/
    │   └── personal-center/
    ├── hook/                   # 前端自定义 Hook
    ├── pages/                  # 页面组件
    ├── stores/                 # Zustand 状态管理
    └── styles/                 # 样式文件
        ├── components/
        └── pages/
```

### 9.2 后端结构

```text
python/
└── app/
    ├── agents/                 # Agent 相关逻辑
    ├── api/                    # WebSocket、Agent 编排等接口相关模块
    ├── config/                 # 配置读取
    ├── core/                   # 核心算法与事件机制
    ├── dao/                    # 数据访问层
    ├── db/                     # 数据库相关模块
    │   └── models/             # 数据模型
    ├── dependencies/           # FastAPI 依赖项
    ├── routers/                # HTTP 路由
    ├── schemas/                # 请求、响应与通用数据结构
    ├── services/               # 服务层，例如大模型调用封装
    ├── utils/                  # 工具函数
    └── main.py                 # FastAPI 应用入口
```

## 10. 当前开发重点

当前阶段的开发重点是学生端学习练习闭环，不优先扩展教师端和管理员端。

优先级如下：

1. 优先完善学生端练习体验
2. 稳定 HTTP 主链路
3. 优化 AI 答题解析质量与 Markdown 展示效果
4. 后续再完善 WebSocket / 全双工通信
5. 教师端和管理员端暂缓

## 11. 开发注意事项

- `.env` 不提交 Git。
- `.env.example` 可以提交。
- `node_modules/` 不提交。
- `.venv/` 不提交。
- 前端不能保存模型密钥。
- 后端启动目录建议为 `python`。
- 前端请求路径不要重复拼接 `/api`。
- README 中的完成情况应随实际开发进度更新。