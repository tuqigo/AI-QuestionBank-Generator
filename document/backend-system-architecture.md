# 后端系统架构文档

## 1. 系统概述

### 1.1 项目简介

**题小宝** - 小学生 AI 题库生成器的后端系统，基于 FastAPI 构建，提供 AI 题目生成、用户认证、历史记录管理等核心功能。

### 1.2 技术选型

| 类别 | 技术 | 版本/说明 |
|------|------|----------|
| Web 框架 | FastAPI | 异步 Python Web 框架 |
| Python 版本 | 3.8+ | 兼容 asyncio 特性 |
| AI API | DashScope (通义千问) | qwen-plus-latest / qwen-vl-plus |
| 数据库 | SQLite | 轻量级嵌入式数据库 |
| 认证 | JWT (python-jose) | HS256 算法，7 天有效期 |
| 密码加密 | bcrypt | 安全哈希 |
| 包管理 | pip + requirements.txt | - |

### 1.3 系统目标

- 提供 RESTful API 供前端调用
- 集成通义千问 AI 进行题目生成
- 管理用户账户和题目历史记录
- 支持管理员后台操作
- 记录 AI 生成日志用于监控分析

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层 (Clients)                        │
├─────────────────────────────────────────────────────────────────┤
│  Web 前端 (React)  │  管理后台  │  移动端 (未来)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                      API 网关层 (API Gateway)                     │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI 应用 (uvicorn)                                          │
│  - CORS 中间件                                                   │
│  - JWT 认证中间件                                                 │
│  - 请求日志                                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (Services)                       │
├─────────────────────────────────────────────────────────────────┤
│  auth  │  questions  │  history  │  extend  │  admin  │  routers │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   数据访问层     │ │   AI 服务层      │ │   工具层        │
│  (Stores)       │ │  (Qwen Client)  │ │  (Utils)        │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ user_store      │ │ qwen_client     │ │ logger          │
│ question_store  │ │ qwen_vision     │ │ validators      │
│ record_store    │ │ batch_manager   │ │ short_id        │
│ admin_log_store │ │                 │ │ json_validator  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据存储层 (Data)                           │
├─────────────────────────────────────────────────────────────────┤
│  SQLite Database (data/users.db)                                │
│  - users                - ai_generation_records                 │
│  - otp_codes            - questions                             │
│  - otp_rate_limit       - admin_operation_logs                  │
│  - user_question_records                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 分层架构说明

#### 2.2.1 API 网关层
- **FastAPI 应用**: 主应用入口，注册所有路由
- **CORS 中间件**: 跨域请求控制，支持 Cloudflare Pages 部署
- **认证中间件**: JWT Token 验证

#### 2.2.2 业务逻辑层 (Routers)
按业务领域划分的路由模块：
- `auth`: 用户认证（注册、登录、找回密码）
- `questions`: 题目生成（结构化/非结构化）
- `history`: 历史记录管理
- `extend`: 图片扩展题
- `admin`: 管理后台

#### 2.2.3 数据访问层 (Stores)
封装数据库操作：
- `user_store`: 用户 CRUD
- `question_store`: 题目数据 CRUD
- `question_record_store`: 题目记录管理
- `ai_generation_record_store`: AI 生成记录

#### 2.2.4 AI 服务层
- `qwen_client`: 通义千问文本生成（支持 Batch 批量调用）
- `qwen_vision`: 通义千问视觉识别（图片题目识别）

---

## 3. 核心模块设计

### 3.1 认证模块

#### 3.1.1 认证流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   用户注册    │────▶│  邮箱 OTP 验证  │────▶│  创建用户    │
└──────────────┘     └──────────────┘     └──────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   用户登录    │────▶│  密码验证    │────▶│  返回 JWT    │
└──────────────┘     └──────────────┘     └──────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  找回密码    │────▶│  邮箱 OTP 验证  │────▶│  重置密码    │
└──────────────┘     └──────────────┘     └──────────────┘
```

#### 3.1.2 OTP 验证码机制

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 有效期 | 5 分钟 | OTP_EXPIRE_MINUTES |
| 最大尝试 | 5 次 | 超过后验证码失效 |
| 速率限制 | 5 次/60 分钟 | 防止短信/邮件轰炸 |

#### 3.1.3 JWT Token

```python
# Token 配置
JWT_SECRET = "your-random-secret"  # 生产环境需修改
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# Payload 结构
{
    "sub": "user@example.com",  # 用户邮箱
    "exp": 1234567890           # 过期时间戳
}
```

### 3.2 题目生成模块

#### 3.2.1 Batch 批量调用机制

为优化 AI 调用成本和响应速度，实现 Batch 批量调用：

```python
# Batch 配置
batch_size = 10          # 每 10 条请求批量提交
max_wait_seconds = 3     # 超时自动提交

# 模型路由
- 简单问题 → qwen-turbo-latest (低成本)
- 复杂问题 → qwen-plus-latest (高质量)
```

#### 3.2.2 题目生成流程

```
用户请求 (prompt)
     │
     ▼
┌─────────────────┐
│  promptValidator│
│  输入校验        │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  添加到 Batch   │
│  队列            │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  等待批量提交    │
│  - 数量触发      │
│  - 超时触发      │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  调用 AI API     │
│  Generation.call│
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  解析 AI 响应    │
│  JSON 校验       │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  数据清洗       │
│  QuestionData   │
│  Cleaner        │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  保存到数据库    │
│  - record       │
│  - questions    │
└─────────────────┘
```

### 3.3 历史记录模块

#### 3.3.1 数据模型

```
user_question_records (题目记录表)
├── id: 主键
├── user_id: 外键 → users.id
├── title: 题目集标题
├── prompt_type: text/image
├── prompt_content: 用户输入
├── ai_response: AI 返回内容
├── short_id: 短 ID（用于分享）
├── share_token: 分享令牌
└── is_deleted: 软删除标记
```

#### 3.3.2 分享机制

```
生成分享链接流程:
1. 生成 share_token (UUID)
2. 保存到 user_question_records.share_token
3. 返回分享 URL: /share/h/{short_id}?token={share_token}

访问分享链接:
1. 验证 token 有效性
2. 查询 share_token 对应的记录
3. 返回题目数据（无需登录）
```

### 3.4 管理员模块

#### 3.4.1 管理员功能

| 功能 | 说明 |
|------|------|
| 用户管理 | 查看用户列表、禁用/启用用户 |
| 记录查看 | 查看用户题目记录、AI 生成记录 |
| 操作日志 | 记录所有管理员操作 |

#### 3.4.2 操作日志

```python
# 日志记录内容
{
    "operator": "admin",
    "action": "disable_user",
    "target_type": "user",
    "target_id": 123,
    "ip": "192.168.1.1",
    "details": "禁用用户 user@example.com"
}
```

---

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────┐       ┌──────────────────────┐
│   users     │       │   otp_codes          │
├─────────────┤       ├──────────────────────┤
│ id (PK)     │       │ id (PK)              │
│ email       │       │ email                │
│ hashed_pwd  │       │ code                 │
│ created_at  │       │ purpose              │
│ is_disabled │       │ expires_at           │
└─────────────┘       └──────────────────────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐       ┌──────────────────────┐
│ user_question_       │       │ ai_generation_       │
│ records              │       │ records              │
├──────────────────────┤       ├──────────────────────┤
│ id (PK)              │       │ id (PK)              │
│ user_id (FK)         │       │ user_id (FK)         │
│ title                │       │ prompt               │
│ prompt_type          │       │ prompt_type          │
│ ai_response          │       │ success              │
│ short_id             │       │ duration             │
│ share_token          │       │ error_message        │
│ is_deleted           │       └──────────────────────┘
└──────────────────────┘
       │
       │ 1:N
       ▼
┌──────────────────────┐
│   questions          │
├──────────────────────┤
│ id (PK)              │
│ record_id (FK)       │
│ question_index       │
│ type                 │
│ stem                 │
│ options (JSON)       │
│ answer_text          │
│ rows_to_answer       │
└──────────────────────┘

┌──────────────────────┐
│ admin_operation_logs │
├──────────────────────┤
│ id (PK)              │
│ operator             │
│ action               │
│ target_type          │
│ created_at           │
└──────────────────────┘
```

### 4.2 表结构说明

详见 [数据库表结构](#附录 - 数据库表结构)

---

## 5. API 设计

### 5.1 API 概览

| 路由前缀 | 说明 | 认证 |
|---------|------|------|
| `/api/auth` | 用户认证 | 部分需要 |
| `/api/questions` | 题目生成 | 需要 |
| `/api/history` | 历史记录 | 需要 |
| `/api/share/history` | 分享接口 | 否 |
| `/api/admin` | 管理后台 | 需要 (Admin) |

### 5.2 核心接口

#### 5.2.1 题目生成

```
POST /api/questions/structured
Request:
{
    "prompt": "小学三年级数学 两位数乘法"
}

Response:
{
    "meta": {
        "subject": "math",
        "grade": "grade3",
        "title": "三年级数学两位数乘法练习"
    },
    "questions": [...],
    "record_id": 123,
    "short_id": "abc123"
}
```

#### 5.2.2 历史记录

```
GET /api/history?cursor=0&size=20

GET /api/history/{short_id}

DELETE /api/history/{short_id}

POST /api/history/{short_id}/share
```

---

## 6. 非功能性设计

### 6.1 性能优化

| 优化点 | 策略 |
|--------|------|
| AI 批量调用 | Batch 管理器，降低 API 调用次数 |
| 数据库索引 | 关键字段建立索引 |
| 分页查询 | 游标分页，避免全表扫描 |
| 并发处理 | 历史记录保存异步化 |

### 6.2 安全设计

| 风险点 | 防护措施 |
|--------|---------|
| 密码存储 | bcrypt 加密 |
| Token 安全 | JWT + HTTPS 传输 |
| OTP 防爆破 | 速率限制 + 尝试次数限制 |
| SQL 注入 | 参数化查询 |
| CORS | 限制允许的来源 |

### 6.3 日志记录

| 日志类型 | 位置 | 说明 |
|---------|------|------|
| API 日志 | api_logger | 请求/响应记录 |
| 认证日志 | auth_logger | 登录/注册行为 |
| 用户日志 | user_logger | 用户操作 |
| AI 日志 | qwen_logger | AI 调用详情 |
| 管理日志 | 数据库 | 管理员操作审计 |

---

## 7. 部署架构

### 7.1 部署环境

```
┌─────────────────┐
│  Cloudflare     │
│  Pages (前端)   │
└─────────────────┘
        │
        │ HTTPS
        ▼
┌─────────────────┐
│  uvicorn        │
│  (FastAPI)      │
│  Port: 8000     │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  SQLite         │
│  (data/)        │
└─────────────────┘
```

### 7.2 环境变量

```bash
# .env 配置
DASHSCOPE_API_KEY=sk-your-api-key
QWEN_MODEL=qwen-plus-latest
JWT_SECRET=your-random-secret
ALLOW_ORIGINS=http://localhost:5173,https://your-domain.com
SMTP_HOST=smtp.163.com
SMTP_USER=your-email
SMTP_PASS=your-password
```

### 7.3 启动命令

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 附录

### A. 数据库表结构

详见 [schema.sql](../backend/sql/schema.sql)

### B. 相关文档
- [后端代码结构](./backend-code-structure.md)
- [前后端交互逻辑](./frontend-backend-interaction-logic.md)
- [前端系统架构](./frontend-system-architecture.md)
