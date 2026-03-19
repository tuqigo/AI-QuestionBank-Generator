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
│  - 全局异常处理                                                   │
│  - 请求日志                                                      │
│  - 健康检查端点 (/health)                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (API Routes)                      │
├─────────────────────────────────────────────────────────────────┤
│  api/v1/                                                         │
│  ├── auth.py         - 用户认证                                 │
│  ├── questions.py    - 题目生成                                 │
│  ├── questions_structured.py - 结构化题目                       │
│  ├── history.py      - 历史记录                                 │
│  ├── extend.py       - 图片扩展题                               │
│  └── admin.py        - 管理后台                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   数据访问层     │ │   AI 服务层      │ │   工具层        │
│  (Services)     │ │  (AI Services)  │ │  (Utils)        │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ user/           │ │ ai/             │ │ logger          │
│ question/       │ │ - qwen_client   │ │ validators      │
│ admin/          │ │ - qwen_vision   │ │ short_id        │
│                 │ │ - data_cleaner  │ │ json_validator  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据存储层 (Data)                           │
├─────────────────────────────────────────────────────────────────┤
│  SQLite Database (data/tixiaobao.db) - 路径统一在 config.py 配置   │
│  - users                - ai_generation_records                 │
│  - otp_codes            - questions                             │
│  - otp_rate_limit       - admin_operation_logs                  │
│  - user_question_records                                        │
│  - question_templates   (2026-03 新增)                          │
│  - template_usage_logs  (2026-03 新增)                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 分层架构说明

#### 2.2.1 API 网关层
- **FastAPI 应用**: 主应用入口，注册所有路由
- **CORS 中间件**: 跨域请求控制，支持 Cloudflare Pages 部署
- **认证中间件**: JWT Token 验证
- **全局异常处理**: 统一错误响应格式
- **健康检查**: `/health` 端点

#### 2.2.2 业务逻辑层 (api/v1/)
按业务领域划分的路由模块：
- `auth.py`: 用户认证（注册、登录、找回密码）
- `questions.py`: 题目生成（非结构化）
- `questions_structured.py`: 结构化题目生成（JSON）
- `history.py`: 历史记录管理（含分享接口）
- `extend.py`: 图片扩展题
- `admin.py`: 管理后台
- `templates.py`: 模板题目生成（2026-03 新增）

#### 2.2.3 服务层 (services/)
按领域分组的业务逻辑：

| 子目录 | 模块 | 说明 |
|--------|------|------|
| `services/ai/` | `qwen_client` | 通义千问文本生成（Batch 批量调用，线程安全） |
| | `qwen_vision` | 通义千问视觉识别 |
| | `question_data_cleaner` | AI 响应数据清洗 |
| `services/user/` | `user_service` | 用户业务逻辑 |
| | `user_store` | 用户数据访问 |
| `services/question/` | `question_service` | 题目业务逻辑 |
| | `question_store` | 题目数据访问 |
| | `question_record_store` | 题目记录管理 |
| | `ai_generation_record_store` | AI 生成记录 |
| `services/admin/` | `admin_auth` | 管理员认证（bcrypt 加密） |
| | `admin_operation_log` | 操作日志记录 |
| `services/template/` | `template_store` | 模板数据访问（2026-03 新增） |
| | `generators/` | 模板生成器（按模板类型分组） |

#### 2.2.4 核心层 (core/)
- `security.py`: JWT、密码加密等安全功能
- `exceptions.py`: 自定义异常类
- `middleware.py`: 全局中间件

#### 2.2.5 数据访问层
封装数据库操作，统一使用 `config.DB_PATH`:

```python
# 所有服务文件使用统一配置
from config import DB_PATH

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

#### 2.2.6 数据库迁移系统（2026-03 新增）

迁移系统独立于应用启动，支持多实例部署：

```
┌─────────────────────────────────────────────────────────────┐
│              数据库迁移系统 (db/migrations/)                 │
├─────────────────────────────────────────────────────────────┤
│  migrations/__init__.py     - 迁移管理器核心逻辑             │
│  migrations_cli.py          - 命令行迁移工具                 │
│  000_create_schema_migrations_table.sql - 迁移元数据表       │
│  001_add_questions_table.sql - 题目表结构                   │
│  002_add_question_templates.sql - 模板系统表                │
│  ...                                                     │
│  MIGRATIONS_GUIDE.md        - 使用指南                       │
│  sync_migration_records.py  - 迁移记录同步脚本               │
└─────────────────────────────────────────────────────────────┘
```

**部署流程**:
```bash
# CI/CD 阶段执行（restart_backend.sh）
# 1. 代码检查
python3 -m py_compile main.py

# 2. 执行迁移（失败则停止部署）
python -m db.migrations_cli migrate

# 3. 重启服务
uvicorn main:app &
```

**核心特性**:
- 幂等性保证：每个迁移脚本只执行一次
- 状态追踪：通过 `schema_migrations` 表记录已执行的迁移
- 事务支持：每个迁移在独立事务中执行，失败自动回滚
- 多实例安全：CI/CD 独立执行，避免并发问题

详见 [数据库迁移系统文档](./database-migrations.md)。

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
JWT_SECRET = os.getenv("JWT_SECRET")  # 必须设置，无默认值
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# Payload 结构
{
    "sub": "user@example.com",  # 用户邮箱
    "exp": 1234567890           # 过期时间戳
}
```

#### 3.1.4 密码策略

- **最小长度**: 8 个字符
- **最大长度**: 32 个字符
- **复杂度要求**: 必须包含字母和数字
- **加密方式**: bcrypt 哈希存储

#### 3.1.5 管理员认证

- **密码存储**: bcrypt 哈希（`ADMIN_PASSWORD_HASH` 环境变量）
- **Token 验证**: 独立的 `decode_admin_token()` 函数
- **操作日志**: 所有管理员操作记录到数据库

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

**线程安全修复** (重构后):

```python
# 问题：_check_timeout 在锁外调用 _submit_batch，存在竞态条件
# 修复：在锁内复制队列，锁外处理批次

def _check_timeout(self):
    while self.is_running:
        time.sleep(0.5)
        batch_to_submit = None
        with self.lock:
            if not self.request_queue:
                continue
            first_req_time = self.request_queue[0].create_time
            elapsed = time.time() - first_req_time
            if elapsed >= self.max_wait_seconds:
                batch_size = min(len(self.request_queue), self.batch_size)
                batch_to_submit = list(self.request_queue)[:batch_size]
                self.request_queue = deque(list(self.request_queue)[batch_size:])
        # 在锁外处理批次
        if batch_to_submit:
            self._process_batch(batch_to_submit)
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

### 3.5 模板题目模块（2026-03 新增）

模板题目系统是一种不依赖 AI 服务的题目生成方式，通过预定义的模板规则和生成器自主生成题目。

#### 3.5.1 系统特点

- **无需 AI 调用**: 完全基于规则的生成，零成本
- **可预测**: 题目格式和内容完全可控
- **高性能**: 毫秒级响应，适合高频使用
- **易扩展**: 每个模板对应独立生成器，符合开闭原则

#### 3.5.2 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    API 层 (/api/templates)                    │
├─────────────────────────────────────────────────────────────┤
│  templates.py                                                │
│  - GET /list     - 获取所有启用的模板列表                     │
│  - POST /generate - 根据模板 ID 生成题目                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   服务层 (services/template/)                 │
├─────────────────────────────────────────────────────────────┤
│  template_store.py                                           │
│  - get_template_by_id()    - 查询模板                         │
│  - get_template_list_items() - 模板列表                       │
│  - create_template()       - 创建模板                         │
│  - update_template()       - 更新模板                         │
│  - delete_template()       - 删除模板                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 生成器层 (generators/)                       │
├─────────────────────────────────────────────────────────────┤
│  base.py          - 抽象基类 TemplateGenerator               │
│  __init__.py      - 生成器注册表 GENERATOR_REGISTRY          │
│  compare_number.py          - 比大小生成器                    │
│  addition_subtraction.py    - 加减法生成器                    │
│  consecutive_addition_subtraction.py - 连加减生成器          │
│  currency_conversion.py     - 人民币换算生成器               │
└─────────────────────────────────────────────────────────────┘
```

#### 3.5.3 生成器接口规范

```python
from abc import ABC, abstractmethod

class TemplateGenerator(ABC):
    @abstractmethod
    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        """
        生成题目

        Args:
            template_config: 模板配置（来自数据库 variables_config 字段）
            quantity: 生成数量
            question_type: 题目类型（来自模板 question_type 字段）

        Returns:
            题目列表，每项包含 type, stem, knowledge_points, rows_to_answer
        """
        pass

    @abstractmethod
    def get_knowledge_points(self, template_config: dict) -> List[str]:
        """获取知识点列表"""
        pass
```

#### 3.5.4 生成器注册表

```python
# generators/__init__.py
GENERATOR_REGISTRY = {
    "compare_number": CompareNumberGenerator,
    "addition_subtraction": AdditionSubtractionGenerator,
    "consecutive_addition_subtraction": ConsecutiveAdditionSubtractionGenerator,
    "currency_conversion": CurrencyConversionGenerator,
}

def get_generator(generator_name: str) -> TemplateGenerator:
    if generator_name not in GENERATOR_REGISTRY:
        raise ValueError(f"未知的生成器：{generator_name}")
    return GENERATOR_REGISTRY[generator_name]()
```

#### 3.5.5 规则约束系统

生成器支持通过规则配置约束题目生成：

| 规则名 | 说明 | 适用生成器 |
|--------|------|----------|
| `ensure_different` | 确保两个数不同 | compare_number |
| `ensure_positive` | 确保减法结果非负（含中间结果） | addition_subtraction, consecutive_addition_subtraction |
| `result_within_10` | 确保结果 ≤ 10 | 所有 |
| `result_within_20` | 确保结果 ≤ 20 | 所有 |
| `result_within_100` | 确保结果 ≤ 100 | 所有 |

#### 3.5.6 题目生成流程

```
POST /api/templates/generate
    │
    ▼
┌─────────────────┐
│  解析模板 ID     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  查询数据库     │
│  获取模板配置    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  获取生成器实例  │
│  get_generator()│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  调用生成器      │
│  generator.     │
│  generate()     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  返回题目列表    │
│  （不保存记录）  │
└─────────────────┘
```

#### 3.5.7 已实现的生成器

**1. CompareNumberGenerator - 比大小**
- 适用：一年级 10 以内数比一比
- 例题：4（）5
- 配置：`a.min`, `a.max`, `b.min`, `b.max`, `rules`

**2. AdditionSubtractionGenerator - 加减法**
- 适用：一年级 10 以内加减法
- 例题：2 + 2 = （ ）
- 配置：`a.min`, `a.max`, `b.min`, `b.max`, `op.values`, `rules`

**3. ConsecutiveAdditionSubtractionGenerator - 连加减**
- 适用：一年级 10 以内连加减
- 例题：2 + 3 + 4 = （ ）
- 特点：检查中间结果非负

**4. CurrencyConversionGenerator - 人民币换算**
- 适用：认识人民币 - 元角分换算
- 例题：50 分 = （ ）角、6 元 = （ ）角、54 元 50 分 = （ ）分
- 换算类型：
  - `yuan_to_jiao` - 元→角
  - `jiao_to_fen` - 角→分
  - `fen_to_jiao` - 分→角
  - `yuan_to_fen` - 元→分
  - `fen_to_yuan` - 分→元
  - `yuan_jiao_to_jiao` - 元 + 角→角
  - `yuan_fen_to_fen` - 元 + 分→分
  - `yuan_jiao_fen_to_fen` - 元 + 角 + 分→分

#### 3.5.8 数据库设计

**question_templates 表**:
```sql
CREATE TABLE question_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- 模板名称
    subject TEXT NOT NULL,        -- 学科：math/chinese/english
    grade TEXT NOT NULL,          -- 年级：grade1~grade9
    semester TEXT NOT NULL,       -- 学期：upper/lower (上学期/下学期)
    textbook_version TEXT NOT NULL, -- 教材版本：人教版/人教版 (新)/北师大版/苏教版/西师版/沪教版/北京版/青岛六三/青岛五四
    question_type TEXT NOT NULL,  -- 题型：CALCULATION/FILL_BLANK
    template_pattern TEXT NOT NULL, -- 模板模式字符串
    variables_config TEXT NOT NULL, -- 变量配置（JSON）
    example TEXT,                 -- 示例
    generator_module TEXT,        -- 生成器模块名
    sort_order INTEGER DEFAULT 0, -- 排序序号
    is_active INTEGER DEFAULT 1,  -- 是否启用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**template_usage_logs 表**:
```sql
CREATE TABLE template_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    generated_params TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES question_templates(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 4. 数据库设计

### 4.1 ER 图

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│     users       │     │   otp_codes      │     │ otp_rate_limit   │
├─────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │     │ id (PK)          │
│ email           │     │ email            │     │ email            │
│ hashed_password │     │ code             │     │ purpose          │
│ grade           │     │ purpose          │     │ ip_address       │
│ created_at      │     │ attempts         │     │ request_count    │
│ is_disabled     │     │ expires_at       │     │ reset_at         │
└─────────────────┘     └──────────────────┘     └──────────────────┘
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
│ prompt_content       │       │ success              │
│ image_path           │       │ duration             │
│ ai_response          │       │ error_message        │
│ short_id             │       │ created_at           │
│ share_token          │       └──────────────────────┘
│ is_deleted           │
│ created_at           │
└──────────────────────┘
        │
        │ 1:N
        ▼
┌──────────────────────┐
│    questions         │
├──────────────────────┤
│ id (PK)              │
│ short_id             │
│ record_id (FK)       │
│ question_index       │
│ type                 │
│ stem                 │
│ options (JSON)       │
│ passage (JSON)       │
│ sub_questions (JSON) │
│ knowledge_points     │
│ answer_blanks        │
│ rows_to_answer       │
│ answer_text          │
│ created_at           │
└──────────────────────┘

┌──────────────────────┐
│ admin_operation_logs │
├──────────────────────┤
│ id (PK)              │
│ operator             │
│ action               │
│ target_type          │
│ target_id            │
│ ip                   │
│ details (JSON)       │
│ created_at           │
└──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│ question_templates   │     │ template_usage_logs  │
├──────────────────────┤     ├──────────────────────┤
│ id (PK)              │     │ id (PK)              │
│ name                 │     │ template_id (FK)     │
│ subject              │     │ user_id (FK)         │
│ grade                │     │ generated_params     │
│ semester             │     │ created_at           │
│ textbook_version     │     └──────────────────────┘
│ question_type        │
│ template_pattern     │
│ variables_config     │
│ example              │
│ generator_module     │
│ sort_order           │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│  knowledge_points    │
├──────────────────────┤
│ id (PK)              │
│ name                 │
│ subject_code         │
│ grade_code           │
│ semester_code        │
│ textbook_version_code│
│ sort_order           │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│    question_types    │
├──────────────────────┤
│ id (PK)              │
│ en_name              │
│ zh_name              │
│ subjects             │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│     subjects         │
├──────────────────────┤
│ id (PK)              │
│ code                 │
│ name_zh              │
│ sort_order           │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│      grades          │
├──────────────────────┤
│ id (PK)              │
│ code                 │
│ name_zh              │
│ sort_order           │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│    semesters         │
├──────────────────────┤
│ id (PK)              │
│ code                 │
│ name_zh              │
│ sort_order           │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│ textbook_versions    │
├──────────────────────┤
│ id (PK)              │
│ version_code         │
│ name_zh              │
│ sort_order           │
│ is_active            │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌──────────────────────┐
│ schema_migrations    │
├──────────────────────┤
│ id (PK)              │
│ version              │
│ filename             │
│ executed_at          │
│ checksum             │
│ status               │
└──────────────────────┘
```

### 4.2 表结构说明

#### 核心业务表

#### users - 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| email | TEXT | 邮箱，唯一 |
| hashed_password | TEXT | bcrypt 密码哈希 |
| grade | TEXT | 用户年级（grade1~grade9） |
| created_at | TIMESTAMP | 创建时间 |
| is_disabled | INTEGER | 禁用标记（0=正常，1=禁用） |

#### otp_codes - OTP 验证码表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| email | TEXT | 邮箱 |
| code | TEXT | 6 位数字验证码 |
| purpose | TEXT | 用途（register/reset_password） |
| attempts | INTEGER | 验证尝试次数（最大 5 次） |
| created_at | TIMESTAMP | 创建时间 |
| expires_at | TIMESTAMP | 过期时间（默认 5 分钟） |

#### otp_rate_limit - OTP 速率限制表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| email | TEXT | 邮箱 |
| purpose | TEXT | 用途 |
| ip_address | TEXT | IP 地址 |
| request_count | INTEGER | 时间窗口内请求次数 |
| reset_at | TIMESTAMP | 计数器重置时间（60 分钟窗口） |

#### user_question_records - 用户题目记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| user_id | INTEGER | 外键 → users.id |
| title | VARCHAR(200) | 题目集标题 |
| prompt_type | VARCHAR(10) | 输入类型（text/image） |
| prompt_content | TEXT | 用户提示词全文 |
| image_path | VARCHAR(500) | 图片路径（图片题） |
| ai_response | TEXT | AI 返回内容（Markdown） |
| short_id | TEXT | 短 ID（分享链接） |
| share_token | VARCHAR(64) | 分享令牌 |
| is_deleted | INTEGER | 软删除（0=正常，1=已删除） |
| created_at | TIMESTAMP | 创建时间 |

#### questions - 题目表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| short_id | TEXT | 短 ID（唯一） |
| record_id | INTEGER | 外键 → user_question_records.id |
| question_index | INTEGER | 题目序号（1, 2, 3...） |
| type | TEXT | 题型（SINGLE_CHOICE/CALCULATION 等） |
| stem | TEXT | 题干内容 |
| options | TEXT | 选项数组（JSON，选择题） |
| passage | TEXT | 阅读材料（JSON，阅读理解/完形填空） |
| sub_questions | TEXT | 子题列表（JSON） |
| knowledge_points | TEXT | 知识点列表（JSON 数组） |
| answer_blanks | INTEGER | 填空题空格数 |
| rows_to_answer | INTEGER | 预留作答行数 |
| answer_text | TEXT | 标准答案 |
| created_at | TIMESTAMP | 创建时间 |

#### ai_generation_records - AI 生成记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| user_id | INTEGER | 外键 → users.id |
| prompt | TEXT | 用户原始提示词 |
| prompt_type | VARCHAR(20) | 提示词类型（text/image） |
| success | INTEGER | 是否成功（1=成功，0=失败） |
| duration | REAL | 耗时（秒） |
| error_message | TEXT | 错误信息 |
| created_at | TIMESTAMP | 创建时间 |

#### admin_operation_logs - 管理员操作日志表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| operator | TEXT | 操作人标识 |
| action | TEXT | 操作类型 |
| target_type | TEXT | 操作对象类型 |
| target_id | INTEGER | 操作对象 ID |
| ip | TEXT | 操作来源 IP |
| details | TEXT | 详细信息（JSON） |
| created_at | TIMESTAMP | 创建时间 |

---

#### 模板系统表

#### question_templates - 题目模板表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | TEXT | 模板名称 |
| subject | TEXT | 学科（math/chinese/english） |
| grade | TEXT | 年级（grade1~grade9） |
| semester | TEXT | 学期（upper/lower） |
| textbook_version | TEXT | 教材版本 |
| question_type | TEXT | 题型 |
| template_pattern | TEXT | 模板模式字符串 |
| variables_config | TEXT | 变量配置（JSON） |
| example | TEXT | 示例题目 |
| generator_module | TEXT | 生成器模块名 |
| sort_order | INTEGER | 排序序号 |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### template_usage_logs - 模板使用记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| template_id | INTEGER | 外键 → question_templates.id |
| user_id | INTEGER | 外键 → users.id |
| generated_params | TEXT | 生成参数（JSON） |
| created_at | TIMESTAMP | 创建时间 |

#### knowledge_points - 知识点表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| name | TEXT | 知识点名称 |
| subject_code | TEXT | 学科代码 |
| grade_code | TEXT | 年级代码 |
| semester_code | TEXT | 学期代码 |
| textbook_version_code | TEXT | 教材版本代码 |
| sort_order | INTEGER | 排序序号 |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

#### 配置表

#### subjects - 学科表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| code | TEXT | 代码（math/chinese/english） |
| name_zh | TEXT | 中文名 |
| sort_order | INTEGER | 排序 |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### grades - 年级表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| code | TEXT | 代码（grade1~grade9） |
| name_zh | TEXT | 中文名（一年级~九年级） |
| sort_order | INTEGER | 排序 |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### semesters - 学期表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| code | TEXT | 代码（upper/lower） |
| name_zh | TEXT | 中文名（上学期/下学期） |
| sort_order | INTEGER | 排序 |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### textbook_versions - 教材版本表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| version_code | TEXT | 版本代码（rjb/bsd/sj 等） |
| name_zh | TEXT | 中文名（人教版/北师大版等） |
| sort_order | INTEGER | 排序 |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

#### question_types - 题型表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| en_name | TEXT | 英文名（唯一） |
| zh_name | TEXT | 中文名 |
| subjects | TEXT | 适用学科（逗号分隔） |
| is_active | INTEGER | 是否启用 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

#### 系统表

#### schema_migrations - 迁移记录表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| version | TEXT | 迁移版本（唯一） |
| filename | TEXT | 迁移文件名 |
| executed_at | TIMESTAMP | 执行时间 |
| checksum | TEXT | 校验和 |
| status | TEXT | 状态（success/failed） |

### 4.3 数据库索引设计

#### 用户相关索引
```sql
-- 用户邮箱查询（登录场景）
CREATE INDEX idx_users_email ON users(email);

-- OTP 验证码验证
CREATE INDEX idx_otp_codes_email ON otp_codes(email, purpose);
CREATE INDEX idx_otp_rate_limit_email ON otp_rate_limit(email, purpose);
```

#### 题目记录相关索引
```sql
-- 用户记录列表查询（主索引）
CREATE INDEX idx_user_question_records_user_deleted
    ON user_question_records(user_id, is_deleted, created_at DESC);

-- 分享链接访问
CREATE INDEX idx_user_question_records_share_token
    ON user_question_records(share_token);

-- 短 ID 快速访问
CREATE INDEX idx_user_question_records_short_id
    ON user_question_records(short_id);
```

#### 题目相关索引
```sql
-- 按试卷 ID 查询题目
CREATE INDEX idx_questions_record_id
    ON questions(record_id, question_index);

-- 短 ID 快速访问
CREATE INDEX idx_questions_short_id
    ON questions(short_id);
```

#### AI 生成记录相关索引
```sql
-- 用户记录筛选
CREATE INDEX idx_ai_generation_records_user_id
    ON ai_generation_records(user_id);

-- 成功/失败统计
CREATE INDEX idx_ai_generation_records_success
    ON ai_generation_records(success);

-- 类型筛选
CREATE INDEX idx_ai_generation_records_prompt_type
    ON ai_generation_records(prompt_type);

-- 时间排序
CREATE INDEX idx_ai_generation_records_created_at
    ON ai_generation_records(created_at DESC);

-- 复合查询优化
CREATE INDEX idx_ai_generation_records_composite
    ON ai_generation_records(user_id, success, prompt_type, created_at DESC);
```

#### 管理员日志相关索引
```sql
-- 按操作类型查询
CREATE INDEX idx_admin_logs_action
    ON admin_operation_logs(action, created_at DESC);

-- 按操作对象查询
CREATE INDEX idx_admin_logs_target
    ON admin_operation_logs(target_type, target_id);
```

#### 知识点相关索引
```sql
-- 多条件筛选
CREATE INDEX idx_kp_filters
    ON knowledge_points(subject_code, grade_code, semester_code, textbook_version_code);

-- 启用状态 + 名称
CREATE INDEX idx_kp_active
    ON knowledge_points(is_active, name);
```

#### 配置表相关索引
```sql
CREATE INDEX idx_subjects_code ON subjects(code, is_active);
CREATE INDEX idx_grades_code ON grades(code, is_active);
CREATE INDEX idx_semesters_code ON semesters(code, is_active);
CREATE INDEX idx_textbook_versions_code ON textbook_versions(version_code, is_active);
```

#### 迁移记录相关索引
```sql
CREATE INDEX idx_schema_migrations_version ON schema_migrations(version);
```

---

### 4.4 数据库路径配置（重构后）

**重构前问题**:
- 每个文件重复定义 `DB_PATH`
- 路径计算复杂 (`parent.parent.parent`)
- 文件移动时需要更新路径逻辑
- 违反 DRY 原则

**重构后方案**:

```python
# config.py
BASE_DIR = Path(__file__).parent  # backend/ 目录
DB_PATH = BASE_DIR / "data" / "users.db"

# 所有服务文件统一导入
from config import DB_PATH

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

**涉及文件** (全部改为 `from config import DB_PATH`):
- `services/user/user_store.py`
- `services/question/question_store.py`
- `services/question/question_record_store.py`
- `services/question/ai_generation_record_store.py`
- `services/admin/admin_operation_log.py`
- `models/otp.py`
- `db/__init__.py`

**优势**:
- 代码减少约 39 行
- 单一职责：路径配置只在一个地方管理
- 易于维护：修改数据库位置只需改一处
- 不易出错：无需计算多层 `parent`

### 4.4 数据库迁移系统（2026-03 新增）

详见 [数据库迁移系统文档](./database-migrations.md)。

**元数据表**:
```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT (datetime('now')),
    checksum TEXT,
    status TEXT DEFAULT 'success'
);
```

**迁移脚本列表**:
```
db/migrations/
├── 000_create_schema_migrations_table.sql    # 迁移元数据表
├── 001_create_users_and_otp_tables.sql       # 用户表、OTP 验证码表
├── 002_create_question_records_tables.sql    # 题目记录表、AI 生成记录表
├── 003_create_questions_table.sql            # 题目表
├── 004_create_admin_logs_table.sql           # 管理员操作日志表
├── 005_create_templates_tables.sql           # 模板表、模板使用记录表
├── 006_create_config_tables.sql              # 配置表（学科/年级/学期/教材版本）
├── 007_create_knowledge_points_table.sql     # 知识点表
├── 008_create_question_types_table.sql       # 题型表
└── ... (后续增量迁移)
```

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
| 模板题目 | 不依赖 AI，毫秒级响应（2026-03） |

### 6.2 安全设计

| 风险点 | 防护措施 |
|--------|---------|
| 密码存储 | bcrypt 加密（用户和管理员） |
| Token 安全 | JWT + HTTPS 传输 |
| OTP 防爆破 | 速率限制 + 尝试次数限制 |
| SQL 注入 | 参数化查询 |
| CORS | 限制允许的来源 |
| API Key 泄露 | 环境变量强制设置，无默认值 |
| 弱密码 | 密码策略（8 字符 + 字母 + 数字） |
| 密钥弱 | JWT_SECRET 强制环境变量验证 |

### 6.3 日志记录

| 日志类型 | 位置 | 说明 |
|---------|------|------|
| API 日志 | api_logger | 请求/响应记录 |
| 认证日志 | auth_logger | 登录/注册行为 |
| 用户日志 | user_logger | 用户操作 |
| AI 日志 | qwen_logger | AI 调用详情 |
| 管理日志 | 数据库 | 管理员操作审计 |

### 6.4 异常处理

**全局异常处理器** (main.py):

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    api_logger.error(f"全局异常：{exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误，请联系管理员"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "请求参数验证失败", "errors": exc.errors()}
    )
```

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
# AI 服务 - 必须设置，无默认值
DASHSCOPE_API_KEY=sk-your-api-key
QWEN_MODEL=qwen-plus-latest
QWEN_VISION_MODEL=qwen-vl-plus

# 认证 - 必须设置，无默认值
JWT_SECRET=your-random-secret  # 使用强随机字符串

# 管理员认证 - bcrypt 哈希
ADMIN_PASSWORD_HASH=$2b$12$...  # bcrypt.hashpw("admin123", bcrypt.gensalt())

# 邮件服务
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your-email@163.com
SMTP_PASS=your-password
SMTP_FROM_NAME=题小宝
SMTP_USE_TLS=true

# OTP 配置
OTP_EXPIRE_MINUTES=5

# CORS 配置
ALLOW_ORIGINS=http://localhost:5173,https://your-domain.com
```

**环境变量验证** (config.py):

```python
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    raise RuntimeError("DASHSCOPE_API_KEY 必须在环境变量中设置")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET 必须在环境变量中设置")
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

详见 [schema.sql](../backend/db/schema.sql)

### B. 安全特性

**环境变量强制验证**:
- `DASHSCOPE_API_KEY` - 无默认值，缺失则启动失败
- `JWT_SECRET` - 无默认值，缺失则启动失败
- `ADMIN_PASSWORD_HASH` - bcrypt 哈希存储

**密码策略**:
- 最小长度：8 字符
- 必须包含：字母 + 数字
- 加密方式：bcrypt

**全局异常处理**:
- 统一错误响应格式
- 详细日志记录
- 友好用户提示

### C. 架构优化 (重构后)

**数据库路径统一配置**:
- 配置位置：`config.py`
- 使用方式：所有服务 `from config import DB_PATH`
- 代码减少：约 39 行

**Batch 管理器线程安全**:
- 问题：锁外调用存在竞态条件
- 修复：锁内复制队列，锁外处理批次

**服务层领域分组**:
- `services/ai/` - AI 服务
- `services/user/` - 用户服务
- `services/question/` - 题目服务
- `services/admin/` - 管理员服务

**模板题目系统** (2026-03 新增):
- 新增 `services/template/` 模块
- 生成器模式 + 注册表模式
- 支持规则约束（ensure_positive, result_within_10 等）
- 已实现 4 个生成器：比大小、加减法、连加减、人民币换算

**数据库迁移系统** (2026-03 新增):
- 新增 `db/migrations/` 模块
- 幂等性保证：每个迁移脚本只执行一次
- 多实例安全：CI/CD 独立执行，避免并发问题
- 集成到 `restart_backend.sh` 部署流程
- 详见 [数据库迁移系统文档](./database-migrations.md)

### D. 相关文档
- [后端代码结构](./backend-code-structure.md)
- [前后端交互逻辑](./frontend-backend-interaction-logic.md)
- [前端系统架构](./frontend-system-architecture.md)
- [模板系统开发指南](./template-system-development.md) (2026-03)
- [数据库迁移系统](./database-migrations.md) (2026-03 新增)
