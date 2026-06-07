# Edu Agent 系统维护模块后端开发交接文档

## 一、模块目标

本阶段只完成“系统维护模块”，用于满足数据库概论大作业第二阶段要求：

```text
维护系统用户账号
维护系统角色
维护系统权限
维护系统菜单
```

系统必须支持：

```text
1. 为用户账号分配角色
2. 每个角色拥有对应系统菜单
3. 每个角色拥有对应系统权限
4. 用户、角色、菜单、权限之间存在明确关联
5. 支持级联删除或软删除
6. 能用 SQL 完成指定查询、修改、删除操作
```

本模块本质是一个 RBAC 权限模型：

```text
User 用户
  ↓
Role 角色
  ↓
Menu 菜单
  ↓
Permission 权限
```

---

## 二、当前系统背景

当前 Edu Agent 已有：

```text
users 表
JWT 登录认证
bcrypt 密码加密
FastAPI
SQLAlchemy Async
PostgreSQL
```

现有 `users` 表继续保留，作为账号表使用。

本阶段需要在现有 `users` 表基础上新增：

```text
roles
menus
permissions
user_roles
role_menus
role_permissions
teachers
students
```

其中：

```text
teachers / students 用于支持“查询所有教师信息”“查询所有学生信息”
联系方式统一放在 users 表中，档案表只保存角色专属信息
```

---

## 三、设计原则

### 1. users 表只负责账号

`users` 表存放所有账号共同属性：

```text
user_id
username
pwd
email
avatar
role
status
created_at
updated_at
```

说明：

```text
users.role 可以继续保留，用于前端快速判断页面渲染。
但数据库作业要求“用户账号分配角色”，所以仍然必须建立 user_roles 关联表。
```

也就是说：

```text
users.role 是前端快捷字段
user_roles 是规范化数据库关联关系
```

两者需要保持一致。

### 2. teachers / students 独立建表

教师和学生有不同业务属性，所以不能只依赖 users.role。

```text
users 1 —— 0/1 teachers
users 1 —— 0/1 students
```

说明：

```text
教师和学生的联系方式统一存储在 users 表中，teachers / students 不再重复保存 phone / email
```

---

## 四、数据库表设计

### 1. roles 角色表

```sql
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL,
    role_code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_roles_is_deleted CHECK (is_deleted IN (0, 1))
);
```

默认角色：

```text
admin       管理员
teacher     教师
student     学生
```

---

### 2. menus 菜单表

```sql
CREATE TABLE menus (
    menu_id SERIAL PRIMARY KEY,
    parent_id INTEGER,
    menu_name VARCHAR(100) NOT NULL,
    menu_code VARCHAR(100) NOT NULL UNIQUE,
    menu_path VARCHAR(200),
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_menus_parent
        FOREIGN KEY (parent_id)
        REFERENCES menus(menu_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_menus_is_deleted CHECK (is_deleted IN (0, 1))
);
```

说明：

```text
parent_id 支持多级菜单
删除父菜单时可级联删除子菜单
```

---

### 3. permissions 权限表

```sql
CREATE TABLE permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) NOT NULL,
    permission_code VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_permissions_is_deleted CHECK (is_deleted IN (0, 1))
);
```

示例权限：

```text
user:view
user:update
role:assign
menu:delete
teacher:view
student:view
```

---

### 4. user_roles 用户角色关联表

```sql
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
        ON DELETE CASCADE
);
```

---

### 5. role_menus 角色菜单关联表

```sql
CREATE TABLE role_menus (
    role_id INTEGER NOT NULL,
    menu_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, menu_id),
    CONSTRAINT fk_role_menus_role
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_role_menus_menu
        FOREIGN KEY (menu_id)
        REFERENCES menus(menu_id)
        ON DELETE CASCADE
);
```

---

### 6. role_permissions 角色权限关联表

```sql
CREATE TABLE role_permissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_role_permissions_role
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_permission
        FOREIGN KEY (permission_id)
        REFERENCES permissions(permission_id)
        ON DELETE CASCADE
);
```

---

### 7. teachers 教师信息表

```sql
CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    teacher_no VARCHAR(50) NOT NULL UNIQUE,
    teacher_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    title VARCHAR(100),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_teachers_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_teachers_is_deleted CHECK (is_deleted IN (0, 1))
);
```

---

### 8. students 学生信息表

```sql
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    student_no VARCHAR(50) NOT NULL UNIQUE,
    student_name VARCHAR(100) NOT NULL,
    major VARCHAR(100),
    grade VARCHAR(50),
    class_name VARCHAR(100),
    is_deleted SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_students_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT chk_students_is_deleted CHECK (is_deleted IN (0, 1))
);
```

---

## 五、表关系说明

```text
users 与 roles 是多对多
通过 user_roles 关联

roles 与 menus 是多对多
通过 role_menus 关联

roles 与 permissions 是多对多
通过 role_permissions 关联

users 与 teachers 是一对零或一
users 与 students 是一对零或一
```

ER 关系：

```text
users —— user_roles —— roles —— role_menus —— menus
                         │
                         └—— role_permissions —— permissions

users —— teachers
users —— students
```

---

## 六、初始化测试数据要求

至少插入：

```text
roles: admin, teacher, student
menus: 不少于 10 条
permissions: 不少于 8 条
users: 不少于 10 条
teachers: 不少于 3 条
students: 不少于 5 条
user_roles: 为每个用户分配角色
role_menus: 为每个角色分配菜单
role_permissions: 为每个角色分配权限
```

示例菜单：

```text
系统首页
用户管理
角色管理
权限管理
菜单管理
课程管理
教学班管理
学生选课
教师开课
学习分析
```

---

## 七、必须完成的 SQL 操作

### 1. 查询某一账户的角色、菜单

```sql
SELECT
    u.user_id,
    u.username,
    r.role_name,
    r.role_code,
    m.menu_name,
    m.menu_code,
    m.menu_path
FROM users u
JOIN user_roles ur ON u.user_id = ur.user_id
JOIN roles r ON ur.role_id = r.role_id
JOIN role_menus rm ON r.role_id = rm.role_id
JOIN menus m ON rm.menu_id = m.menu_id
WHERE u.username = 'admin'
  AND r.is_deleted = 0
  AND m.is_deleted = 0;
```

---

### 2. 查询对应角色下有多少用户

```sql
SELECT
    r.role_name,
    r.role_code,
    COUNT(ur.user_id) AS user_count
FROM roles r
LEFT JOIN user_roles ur ON r.role_id = ur.role_id
WHERE r.role_code = 'student'
  AND r.is_deleted = 0
GROUP BY r.role_id, r.role_name, r.role_code;
```

---

### 3. 查询所有教师信息

```sql
SELECT
    t.teacher_id,
    t.teacher_no,
    t.teacher_name,
    t.department,
    t.title,
    u.username,
    u.email
FROM teachers t
JOIN users u ON t.user_id = u.user_id
WHERE t.is_deleted = 0;
```

---

### 4. 查询所有学生信息

```sql
SELECT
    s.student_id,
    s.student_no,
    s.student_name,
    s.major,
    s.grade,
    s.class_name,
    u.username,
    u.email
FROM students s
JOIN users u ON s.user_id = u.user_id
WHERE s.is_deleted = 0;
```

---

### 5. 查询某个用户的账号密码

```sql
SELECT
    user_id,
    username,
    pwd
FROM users
WHERE username = 'Rainie';
```

注意：

```text
pwd 应该是 bcrypt 哈希，不应是明文密码。
```

---

### 6. 修改一个用户的密码

开发中应通过后端 hash_password 生成哈希后再更新。

SQL 示例：

```sql
UPDATE users
SET
    pwd = '$2b$12$example_bcrypt_hash_value',
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'Rainie';
```

---

### 7. 删除两条不再需要的菜单信息

如果使用物理删除，依赖 ON DELETE CASCADE：

```sql
DELETE FROM menus
WHERE menu_code IN ('old_menu_1', 'old_menu_2');
```

如果使用软删除，推荐：

```sql
UPDATE menus
SET
    is_deleted = 1,
    updated_at = CURRENT_TIMESTAMP
WHERE menu_code IN ('old_menu_1', 'old_menu_2');
```

报告中可以说明：

```text
系统实际业务采用软删除，外键表保留历史数据；数据库表仍配置级联删除以满足关联删除要求。
```

---

### 8. 修改某个用户的角色为教师

如果一个用户只允许一个主角色：

```sql
DELETE FROM user_roles
WHERE user_id = (
    SELECT user_id FROM users WHERE username = 'Rainie'
);

INSERT INTO user_roles(user_id, role_id)
SELECT u.user_id, r.role_id
FROM users u, roles r
WHERE u.username = 'Rainie'
  AND r.role_code = 'teacher';
```

同步更新 users.role 快捷字段：

```sql
UPDATE users
SET
    role = 'teacher',
    updated_at = CURRENT_TIMESTAMP
WHERE username = 'Rainie';
```

如果允许一个用户多个角色，则不要 DELETE，只 INSERT 新角色。

---

## 八、后端开发目录建议

根据现有项目结构，新增或补充：

```text
app/db/models/role.py
app/db/models/menu.py
app/db/models/permission.py
app/db/models/user_role.py
app/db/models/role_menu.py
app/db/models/role_permission.py
app/db/models/teacher.py
app/db/models/student.py

app/schemas/system.py
app/dao/system_dao.py
app/services/system_service.py
app/routers/system.py
```

---

## 九、后端 API 设计

统一前缀：

```text
/api/system
```

### 1. 查询用户角色菜单

```text
GET /api/system/users/{user_id}/roles-menus
```

返回：

```json
{
  "user_id": 1,
  "username": "admin",
  "roles": [
    {
      "role_id": 1,
      "role_name": "管理员",
      "role_code": "admin"
    }
  ],
  "menus": [
    {
      "menu_id": 1,
      "menu_name": "用户管理",
      "menu_code": "user_manage",
      "menu_path": "/system/users"
    }
  ]
}
```

---

### 2. 查询角色用户数量

```text
GET /api/system/roles/{role_id}/user-count
```

返回：

```json
{
  "role_id": 3,
  "role_name": "学生",
  "role_code": "student",
  "user_count": 20
}
```

---

### 3. 查询所有教师

```text
GET /api/system/teachers
```

---

### 4. 查询所有学生

```text
GET /api/system/students
```

---

### 5. 查询用户账号信息

```text
GET /api/system/users/{user_id}/account
```

返回：

```json
{
  "user_id": 1,
  "username": "Rainie",
  "pwd": "$2b$12$..."
}
```

注意：真实系统不建议返回密码哈希，但为了课程 SQL 演示可以保留数据库查询；API 可不暴露 pwd。

---

### 6. 修改用户密码

```text
PUT /api/system/users/{user_id}/password
```

请求：

```json
{
  "new_pwd": "123aaa"
}
```

后端必须：

```text
hash_password(new_pwd)
再更新 users.pwd
```

---

### 7. 删除菜单

```text
DELETE /api/system/menus/{menu_id}
```

建议实现为软删除：

```text
menus.is_deleted = 1
```

---

### 8. 修改用户角色为教师

```text
PUT /api/system/users/{user_id}/role
```

请求：

```json
{
  "role_code": "teacher"
}
```

后端逻辑：

```text
1. 查询 user 是否存在
2. 查询 role_code 对应 role 是否存在
3. 删除原 user_roles
4. 插入新 user_roles
5. 同步更新 users.role
```

---

## 十、Service 层业务逻辑

### SystemService.get_user_roles_menus(user_id)

流程：

```text
1. 查询用户
2. 查询用户角色
3. 根据角色查询菜单
4. 去重菜单
5. 返回用户、角色、菜单结构
```

---

### SystemService.get_role_user_count(role_id)

流程：

```text
1. 查询角色是否存在
2. COUNT user_roles
3. 返回角色和数量
```

---

### SystemService.list_teachers()

流程：

```text
JOIN teachers + users
过滤 teachers.is_deleted = 0
```

---

### SystemService.list_students()

流程：

```text
JOIN students + users
过滤 students.is_deleted = 0
```

---

### SystemService.change_user_password(user_id, new_pwd)

流程：

```text
1. 查询用户是否存在
2. 使用 hash_password 生成 bcrypt 密码
3. 更新 users.pwd
4. 返回成功
```

---

### SystemService.delete_menu(menu_id)

流程：

```text
1. 查询菜单是否存在
2. 将 menus.is_deleted 改为 1
3. 同时可选择将子菜单 is_deleted 改为 1
```

---

### SystemService.change_user_role(user_id, role_code)

流程：

```text
1. 查询用户是否存在
2. 查询角色是否存在
3. 删除 user_roles 中该用户旧角色
4. 插入新角色
5. 更新 users.role = role_code
6. 提交事务
```

---

## 十一、DAO 层方法建议

```python
class SystemDAO:
    async def get_user_by_id(db, user_id): ...
    async def get_role_by_code(db, role_code): ...
    async def get_user_roles(db, user_id): ...
    async def get_user_menus(db, user_id): ...
    async def count_users_by_role(db, role_id): ...
    async def list_teachers(db): ...
    async def list_students(db): ...
    async def update_user_password(db, user_id, hashed_pwd): ...
    async def soft_delete_menu(db, menu_id): ...
    async def replace_user_role(db, user_id, role_id): ...
```

DAO 只写数据库操作，不写复杂业务规则。

---

## 十二、Pydantic Schema 建议

```python
class ChangePasswordRequest(BaseModel):
    new_pwd: str

class ChangeUserRoleRequest(BaseModel):
    role_code: str

class RoleResponse(BaseModel):
    role_id: int
    role_name: str
    role_code: str

class MenuResponse(BaseModel):
    menu_id: int
    menu_name: str
    menu_code: str
    menu_path: str | None = None

class UserRolesMenusResponse(BaseModel):
    user_id: int
    username: str
    roles: list[RoleResponse]
    menus: list[MenuResponse]
```

如果当前环境是 Python 3.9，应使用：

```python
from typing import Optional, List

menu_path: Optional[str] = None
roles: List[RoleResponse]
menus: List[MenuResponse]
```

不要使用 Python 3.10 的 `str | None`。

---

## 十三、权限控制建议

本阶段后端接口先实现业务，不强制完整权限拦截。

但建议预留：

```text
只有 admin 可以访问 /api/system/**
```

如果已有 JWT 当前用户依赖，可增加：

```python
Depends(get_current_user)
```

后续可判断：

```text
current_user.role == "admin"
```

---

## 十四、开发验收标准

完成后必须能演示：

```text
1. 查询 admin 账号拥有的角色和菜单
2. 查询 student 角色下有多少用户
3. 查询所有教师信息
4. 查询所有学生信息
5. 查询 Rainie 的账号密码哈希
6. 修改 Rainie 的密码
7. 删除两个菜单
8. 修改 Rainie 的角色为 teacher
```

同时数据库中必须能看到：

```text
users
roles
menus
permissions
user_roles
role_menus
role_permissions
teachers
students
```

这些表之间存在外键关联。

---

## 十五、交付文件建议

建议新增：

```text
sql/system_maintenance_create_tables.sql
sql/system_maintenance_insert_data.sql
sql/system_maintenance_required_queries.sql
```

后端新增：

```text
app/routers/system.py
app/services/system_service.py
app/dao/system_dao.py
app/schemas/system.py
```

模型新增：

```text
app/db/models/role.py
app/db/models/menu.py
app/db/models/permission.py
app/db/models/teacher.py
app/db/models/student.py
```

---

## 十六、最终说明

本模块是管理员后台维护模块，主要用于证明系统具备：

```text
用户账号维护能力
角色分配能力
权限菜单关联能力
教师学生信息维护能力
SQL 多表关联查询能力
级联删除或软删除能力
```

不要把它做成单纯前端 role 字段判断。课程作业的重点是数据库表之间的关系和 SQL 操作。
