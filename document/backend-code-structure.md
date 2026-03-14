# 后端代码结构文档

## 1. 项目概述

### 1.1 基本信息

- **项目名称**: 题小宝 - 小学生 AI 题库生成器（后端）
- **技术栈**: FastAPI + Python 3.8 + SQLite
- **AI 服务**: DashScope (通义千问)

### 1.2 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DASHSCOPE_API_KEY 等配置

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 2. 目录结构

### 2.1 完整目录树

```
backend/
├── data/                       # 数据库文件目录（运行时创建）
│   └── users.db
│
├── models/                     # 数据模型层
│   ├── __init__.py
│   ├── user.py                 # 用户模型（UserCreate, UserLogin, UserInDB）
│   ├── admin.py                # 管理员模型
│   ├── otp.py                  # OTP 验证码模型
│   ├── structured_question.py  # 结构化题目模型
│   ├── question_record.py      # 题目记录模型
│   ├── ai_generation_record.py # AI 生成记录模型
│   └── admin_operation_log.py  # 管理员操作日志模型
│
├── routers/                    # 路由控制器层
│   ├── __init__.py
│   ├── auth.py                 # 用户认证路由（登录/注册/找回密码）
│   ├── questions.py            # 题目生成路由（非结构化）
│   ├── questions_structured.py # 结构化题目生成路由
│   ├── history.py              # 历史记录路由（含分享接口）
│   ├── extend.py               # 图片扩展题路由
│   └── admin.py                # 管理后台路由
│
├── services/                   # 业务逻辑层
│   ├── __init__.py
│   ├── auth.py                 # JWT 认证服务
│   ├── admin_auth.py           # 管理员认证
│   ├── user_store.py           # 用户数据访问
│   ├── question_store.py       # 题目数据访问
│   ├── question_record_store.py# 题目记录存储
│   ├── ai_generation_record_store.py  # AI 生成记录存储
│   ├── admin_operation_log.py  # 管理员操作日志
│   ├── qwen_client.py          # 通义千问客户端（Batch 批量调用）
│   ├── qwen_vision.py          # 通义千问视觉识别
│   ├── email_sender.py         # 邮件发送服务
│   └── question_data_cleaner.py# 题目数据清洗
│
├── sql/                        # 数据库 SQL 脚本
│   ├── __init__.py             # 数据库初始化入口
│   ├── schema.sql              # 表结构定义
│   └── migrations/             # 数据库迁移脚本
│       └── 001_add_questions_table.sql
│
├── utils/                      # 工具函数层
│   ├── logger.py               # 日志配置（多 logger 实例）
│   ├── validators.py           # 输入校验函数
│   ├── json_validator.py       # JSON Schema 校验
│   └── short_id.py             # 短 ID 生成
│
├── config.py                   # 全局配置（从 .env 读取）
├── config copy.py              # 配置备份（可删除）
├── main.py                     # FastAPI 应用入口
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量（不提交到 git）
└── .env.example                # 环境变量模板
```

### 2.2 目录组织原则

#### 分层架构 (Layered Architecture)

```
backend/
├── routers/        # 路由层：处理 HTTP 请求/响应
├── services/       # 服务层：业务逻辑实现
├── models/         # 模型层：数据结构定义
├── utils/          # 工具层：通用辅助函数
└── sql/            # 数据层：SQL 脚本
```

**优点**:
- 职责清晰：每层有明确的职责边界
- 易于测试：各层可独立单元测试
- 易于维护：修改影响范围可控

---

## 3. 核心模块说明

### 3.1 入口文件

#### main.py
FastAPI 应用入口：

```python
# 核心功能
- 创建 FastAPI 应用实例
- 配置 CORS 中间件
- 初始化数据库
- 注册所有路由
```

#### config.py
全局配置管理：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DASHSCOPE_API_KEY | 通义千问 API Key | - |
| QWEN_MODEL | 文本生成模型 | qwen-plus-latest |
| JWT_SECRET | JWT 密钥 | change-me-in-production |
| JWT_EXPIRE_MINUTES | Token 有效期 | 10080 (7 天) |
| SMTP_HOST | SMTP 服务器 | smtp.163.com |
| SMTP_USER | 邮箱账号 | - |
| QUESTION_SYSTEM_PROMPT | AI 系统提示词 | - |

### 3.2 路由模块 (routers/)

#### auth.py - 用户认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/send-otp` | POST | 发送邮箱验证码 |
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/reset-password` | POST | 重置密码 |
| `/api/auth/me` | GET | 获取当前用户 |
| `/api/auth/logout` | POST | 登出 |

#### questions.py - 题目生成

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/questions/generate` | POST | 生成题目（非结构化） |

#### questions_structured.py - 结构化题目生成

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/questions/structured` | POST | 生成结构化题目（JSON） |

#### history.py - 历史记录

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/history` | GET | 获取历史记录列表 |
| `/api/history/{short_id}` | GET | 获取单条记录详情 |
| `/api/history/{short_id}` | DELETE | 删除记录 |
| `/api/history/{short_id}/share` | POST | 生成分享链接 |
| `/api/history/{short_id}/questions` | GET | 获取试卷题目 |
| `/api/history/{short_id}/answers` | GET | 获取整卷答案 |

#### extend.py - 图片扩展题

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/questions/extend-from-image` | POST | 上传图片生成扩展题 |

#### admin.py - 管理后台

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/login` | POST | 管理员登录 |
| `/api/admin/me` | GET | 获取管理员状态 |
| `/api/admin/users` | GET | 用户列表 |
| `/api/admin/users/{user_id}` | GET | 用户详情 |
| `/api/admin/users/{user_id}/disable` | POST | 禁用/启用用户 |
| `/api/admin/users/{user_id}/records` | GET | 用户题目记录 |
| `/api/admin/operation-logs` | GET | 操作日志列表 |
| `/api/admin/ai-records` | GET | AI 生成记录列表 |

### 3.3 服务模块 (services/)

#### 认证服务

**auth.py** - JWT 认证：
```python
def verify_password(plain, hashed) -> bool
def get_password_hash(password) -> str
def create_access_token(data: dict) -> str
def decode_token(token: str) -> Optional[str]
```

**admin_auth.py** - 管理员认证：
```python
def verify_admin_password(password) -> bool
def create_admin_token() -> str
def decode_admin_token(token) -> Optional[str]
```

#### 数据访问服务

**user_store.py** - 用户数据访问：
```python
def get_user(email) -> Optional[UserInDB]
def create_user(email, password) -> UserInDB
def update_password(email, new_password) -> bool
def get_all_users(page, page_size) -> Tuple[List, int, bool]
def set_user_disabled(user_id, is_disabled) -> bool
```

**question_store.py** - 题目数据访问：
```python
def get_questions_by_record_id(record_id) -> List[dict]
def get_question_by_id(question_id) -> Optional[dict]
def get_question_answer(question_id) -> Optional[dict]
def batch_insert_questions(record_id, questions) -> List
```

**question_record_store.py** - 题目记录存储：
```python
def create_record(user_id, record) -> Tuple[int, str]
def get_record_by_short_id(short_id, user_id) -> Optional
def get_user_records(user_id, cursor, size) -> Tuple[List, int, bool]
def soft_delete_record(record_id, user_id) -> bool
def generate_share_token(record_id, user_id) -> str
```

#### AI 服务

**qwen_client.py** - 通义千问客户端：

```python
# 核心类
class QwenBatchManager:
    """Batch 请求管理器
    - 数量触发：攒够 batch_size 条立即提交
    - 超时触发：距离首个请求超过 max_wait_seconds 自动提交
    """

# 主要函数
def generate_questions_async(user_prompt, user_id) -> Tuple[str, str]
def _call_model_batch(model_name, batch_requests) -> None
```

**qwen_vision.py** - 视觉识别：
```python
def analyze_image(image_path, prompt) -> str
```

#### 工具服务

**email_sender.py** - 邮件发送：
```python
def send_otp_email(email, code, expire_minutes, subject_prefix) -> bool
```

**question_data_cleaner.py** - 数据清洗：
```python
class QuestionDataCleaner:
    @staticmethod
    def parse_ai_response(content) -> Tuple[MetaData, List[dict]]
```

### 3.4 模型模块 (models/)

#### user.py
```python
class UserCreate(BaseModel)      # 注册请求
class UserLogin(BaseModel)       # 登录请求
class UserInDB(BaseModel)        # 数据库用户
class TokenResponse(BaseModel)   # Token 响应
class EmailOtpRequest(BaseModel) # OTP 请求
class ResetPasswordRequest(BaseModel)
```

#### structured_question.py
```python
class MetaData(BaseModel)        # 题目元数据
class Question(BaseModel)        # 单道题目
class QuestionBank(BaseModel)    # 完整题库
```

#### question_record.py
```python
class QuestionRecordCreate(BaseModel)   # 创建记录
class QuestionRecordResponse(BaseModel) # 记录响应
class QuestionRecordListResponse(BaseModel)
class ShareTokenResponse(BaseModel)
```

### 3.5 工具模块 (utils/)

#### logger.py
多 logger 实例配置：

| Logger | 用途 |
|--------|------|
| api_logger | API 请求日志 |
| auth_logger | 认证相关日志 |
| user_logger | 用户操作日志 |
| qwen_logger | AI 调用日志 |
| admin_logger | 管理员日志 |

#### validators.py
```python
def validate_prompt(prompt) -> Optional[str]
    """验证提示词，返回错误消息"""
```

#### json_validator.py
```python
def validate_question_json(content) -> Tuple[bool, dict, list]
def validate_question_data(data) -> Tuple[bool, QuestionBank, list]
def extract_question_text(question) -> str
```

#### short_id.py
```python
def generate_short_id() -> str
    """生成 8 位短 ID"""
```

---

## 4. 数据库操作

### 4.1 数据库连接

```python
# 统一连接管理
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 字典式访问
    return conn
```

### 4.2 初始化流程

```python
# sql/__init__.py
def init_database():
    # 1. 创建 data 目录
    # 2. 连接数据库
    # 3. 执行 schema.sql
    # 4. 提交并关闭
```

### 4.3 迁移管理

```
sql/migrations/
└── 001_add_questions_table.sql  # 添加 questions 表
```

---

## 5. 代码规范

### 5.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件/目录 | snake_case | `question_record_store.py` |
| 函数/变量 | snake_case | `def get_user()` |
| 类 | PascalCase | `class QuestionRecord` |
| 常量 | UPPER_SNAKE_CASE | `JWT_EXPIRE_MINUTES` |
| 私有函数 | 前缀 `_` | `def _validate()` |

### 5.2 日志规范

```python
# 日志级别使用
logger.debug()    # 调试信息（详细执行过程）
logger.info()     # 一般信息（关键节点）
logger.warning()  # 警告（不影响主流程的异常）
logger.error()    # 错误（影响主流程的异常）
```

### 5.3 错误处理

```python
# 统一异常处理模式
try:
    # 业务逻辑
except ValueError as e:
    # 配置错误/数据错误
    raise HTTPException(status_code=400, detail=str(e))
except RuntimeError as e:
    # API 错误
    raise HTTPException(status_code=502, detail=str(e))
except Exception as e:
    # 未知错误
    api_logger.error(f"未知错误：{e}")
    raise HTTPException(status_code=500, detail="系统错误")
```

---

## 6. 配置说明

### 6.1 .env 配置

```bash
# AI 服务
DASHSCOPE_API_KEY=sk-your-api-key
QWEN_MODEL=qwen-plus-latest
QWEN_VISION_MODEL=qwen-vl-plus

# 认证
JWT_SECRET=your-random-secret

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

# 运营配置
TARGET_USER_IDS=1,2,3
```

---

## 7. 运行与调试

### 7.1 开发模式

```bash
# 启动开发服务器（热重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 访问 API 文档

FastAPI 自动生成 Swagger UI：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 7.3 日志查看

日志输出到控制台，格式：
```
2024-01-01 12:00:00 - api_logger - INFO - 题目生成请求，email: user@example.com
```

---

## 8. 测试

### 8.1 单元测试（待完善）

```bash
# 运行测试（pytest）
pytest tests/
```

### 8.2 接口测试

使用 Swagger UI 或 Postman 测试各接口。

---

## 附录

### A. 依赖包说明

| 包名 | 用途 |
|------|------|
| fastapi | Web 框架 |
| uvicorn | ASGI 服务器 |
| pydantic | 数据验证 |
| python-jose | JWT 编解码 |
| bcrypt | 密码加密 |
| python-dotenv | 环境变量管理 |
| dashscope | 通义千问 SDK |
| aiosmtplib | 异步邮件发送 |

### B. 相关文档
- [后端系统架构](./backend-system-architecture.md)
- [前后端交互逻辑](./frontend-backend-interaction-logic.md)
