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
│   ├── structured_question.py  # 结构化题目模型（QuestionBank, Question, MetaData）
│   ├── question_record.py      # 题目记录模型
│   ├── ai_generation_record.py # AI 生成记录模型
│   ├── admin_operation_log.py  # 管理员操作日志模型
│   └── question_template.py    # 题目模板模型（2026-03 新增）
│
├── api/                        # API 路由层（原 routers/）
│   ├── __init__.py
│   ├── deps.py                 # 统一依赖注入（认证、权限）
│   └── v1/
│       ├── auth.py             # 用户认证路由（登录/注册/找回密码）
│       ├── questions.py        # 题目生成路由（非结构化）
│       ├── questions_structured.py  # 结构化题目生成路由
│       ├── history.py          # 历史记录路由（含分享接口）
│       ├── extend.py           # 图片扩展题路由
│       ├── admin.py            # 管理后台路由
│       └── templates.py        # 模板题目路由（2026-03 新增）
│
├── services/                   # 业务逻辑层（按领域分组）
│   ├── __init__.py
│   ├── ai/                     # AI 服务
│   │   ├── qwen_client.py      # 通义千问客户端（Batch 批量调用，线程安全）
│   │   ├── qwen_vision.py      # 通义千问视觉识别
│   │   └── question_data_cleaner.py  # 题目数据清洗
│   ├── user/                   # 用户服务
│   │   ├── user_service.py     # 用户业务逻辑
│   │   └── user_store.py       # 用户数据访问
│   ├── question/               # 题目服务
│   │   ├── question_service.py # 题目业务逻辑
│   │   ├── question_store.py   # 题目数据访问
│   │   ├── question_record_store.py  # 题目记录存储
│   │   └── ai_generation_record_store.py  # AI 生成记录存储
│   ├── admin/                  # 管理员服务
│   │   ├── admin_auth.py       # 管理员认证（bcrypt 加密）
│   │   └── admin_operation_log.py  # 管理员操作日志
│   └── template/               # 模板题目服务（2026-03 新增）
│       ├── __init__.py
│       ├── template_store.py   # 模板数据访问
│       └── generators/         # 模板生成器（按模板类型分组）
│           ├── __init__.py     # 生成器注册表
│           ├── base.py         # 生成器抽象基类
│           ├── compare_number.py           # 比大小生成器
│           ├── addition_subtraction.py     # 加减法生成器
│           ├── consecutive_addition_subtraction.py  # 连加减生成器
│           └── currency_conversion.py      # 人民币换算生成器
│
├── db/                         # 数据层（原 sql/）
│   ├── __init__.py             # 数据库初始化入口
│   ├── schema.sql              # 表结构定义
│   └── migrations/             # 数据库迁移脚本
│       ├── 001_add_questions_table.sql
│       └── 002_add_question_templates.sql  # 模板系统表（2026-03 新增）
│
├── utils/                      # 工具函数层
│   ├── __init__.py
│   ├── logger.py               # 日志配置（多 logger 实例）
│   ├── validators.py           # 输入校验函数
│   ├── json_validator.py       # JSON Schema 校验
│   └── short_id.py             # 短 ID 生成
│
├── core/                       # 核心模块
│   ├── security.py             # 安全相关（JWT、密码加密）
│   ├── exceptions.py           # 自定义异常类
│   └── middleware.py           # 全局中间件
│
├── config.py                   # 全局配置（环境变量、数据库路径）
├── main.py                     # FastAPI 应用入口（含全局异常处理）
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量（不提交到 git）
└── .env.example                # 环境变量模板
```

### 2.2 目录组织原则

#### 分层架构 (Layered Architecture)

```
backend/
├── api/            # 路由层：处理 HTTP 请求/响应
├── core/           # 核心层：安全、异常、中间件
├── services/       # 服务层：业务逻辑实现（按领域分组）
├── models/         # 模型层：数据结构定义
├── utils/          # 工具层：通用辅助函数
├── db/             # 数据层：SQL 脚本、数据库初始化
└── config.py       # 配置层：统一配置管理
```

**优点**:
- 职责清晰：每层有明确的职责边界
- 易于测试：各层可独立单元测试
- 易于维护：修改影响范围可控
- 领域分组：同领域代码集中，便于导航

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
| DASHSCOPE_API_KEY | 通义千问 API Key | **无** (必须设置) |
| QWEN_MODEL | 文本生成模型 | qwen-plus-latest |
| JWT_SECRET | JWT 密钥 | **无** (必须设置) |
| JWT_EXPIRE_MINUTES | Token 有效期 | 10080 (7 天) |
| SMTP_HOST | SMTP 服务器 | smtp.163.com |
| SMTP_USER | 邮箱账号 | - |
| ADMIN_PASSWORD_HASH | 管理员密码哈希 | - |
| QUESTION_SYSTEM_PROMPT | AI 系统提示词 | - |

**重要**:
- `DASHSCOPE_API_KEY` 和 `JWT_SECRET` 必须通过环境变量设置，启动时验证
- 管理员密码使用 bcrypt 哈希存储，不保存明文
- 数据库路径 `DB_PATH` 统一在此配置，所有服务通过 `from config import DB_PATH` 使用

### 3.2 路由模块 (api/v1/)

#### auth.py - 用户认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/send-otp` | POST | 发送邮箱验证码 |
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/reset-password` | POST | 重置密码 |
| `/api/auth/me` | GET | 获取当前用户（含 grade 年级字段） |
| `/api/auth/logout` | POST | 登出 |

#### users.py - 用户信息

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/users/grade` | PUT | 更新用户年级（grade1~grade9） |

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

#### templates.py - 模板题目（2026-03 新增）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/templates/list` | GET | 获取所有启用的模板列表 |
| `/api/templates/generate` | POST | 根据模板 ID 生成题目（无需 AI） |

**特点**:
- 不依赖 AI 服务，后台自主生成题目
- 题目不保存历史记录，一次性使用
- 每个模板对应独立生成器，便于扩展

### 3.3 服务模块 (services/)

服务层按领域分组为四个子目录：

```
services/
├── ai/         # AI 服务（Qwen 客户端、数据清洗）
├── user/       # 用户服务（认证、存储）
├── question/   # 题目服务（生成、存储、记录）
└── admin/      # 管理员服务（认证、日志）
```

#### AI 服务 (services/ai/)

**qwen_client.py** - 通义千问客户端（线程安全）：

```python
# 核心类
class QwenBatchManager:
    """Batch 请求管理器
    - 数量触发：攒够 batch_size 条立即提交
    - 超时触发：距离首个请求超过 max_wait_seconds 自动提交
    - 线程安全：锁内复制队列，锁外处理批次
    """

# 主要函数
def generate_questions_async(user_prompt, user_id) -> Tuple[str, str]
def _call_model_batch(model_name, batch_requests) -> None
def _process_batch(batch_requests: List[_BatchRequest]) -> None  # 线程安全
```

**qwen_vision.py** - 视觉识别：
```python
def analyze_image(image_path, prompt) -> str
```

**question_data_cleaner.py** - 数据清洗：
```python
class QuestionDataCleaner:
    @staticmethod
    def parse_ai_response(content) -> Tuple[MetaData, List[dict]]
```

#### 用户服务 (services/user/)

**user_service.py** - 用户业务逻辑：
```python
# 用户相关业务逻辑封装
```

**user_store.py** - 用户数据访问：
```python
def get_user(email) -> Optional[UserInDB]
def create_user(email, password) -> UserInDB
def update_password(email, new_password) -> bool
def get_all_users(page, page_size) -> Tuple[List, int, bool]
def set_user_disabled(user_id, is_disabled) -> bool
def update_user_grade(user_id, grade) -> bool  # 更新用户年级
```

#### 题目服务 (services/question/)

**question_service.py** - 题目业务逻辑：
```python
# 题目相关业务逻辑封装
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

**ai_generation_record_store.py** - AI 生成记录存储：
```python
def create_record(record: AiGenerationRecordCreate) -> int
def get_record_by_id(record_id: int) -> Optional[AiGenerationRecordResponse]
def get_records(filter, page, page_size) -> Tuple[List, int, bool]
def get_user_records(user_id, page, page_size) -> Tuple[List, int, bool]
def get_statistics_by_user(user_id: int) -> dict
```

#### 管理员服务 (services/admin/)

**admin_auth.py** - 管理员认证（bcrypt 加密）：
```python
# 密码使用 bcrypt 哈希存储
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")

def verify_admin_password(password) -> bool:
    return bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())

def create_admin_token() -> str
def decode_admin_token(token) -> Optional[str]
```

**admin_operation_log.py** - 管理员操作日志：
```python
def log_operation(operator, action, target_type, target_id, ip, details) -> int
def get_operation_logs(page, page_size) -> Tuple[List[dict], int, bool]
def get_logs_by_target(target_type, target_id) -> List[dict]
```

#### 模板服务 (services/template/)（2026-03 新增）

**template_store.py** - 模板数据访问：
```python
def get_template_by_id(template_id: int) -> Optional[QuestionTemplate]
def get_template_list_items() -> List[QuestionTemplateListItem]
def create_template(...) -> int
def update_template(template_id: int, ...) -> bool
def delete_template(template_id: int) -> bool
```

**generators/** - 模板生成器目录：
- `base.py` - 抽象基类 `TemplateGenerator`
- `__init__.py` - 生成器注册表 `GENERATOR_REGISTRY`
- `compare_number.py` - 比大小生成器（一年级 10 以内）
- `addition_subtraction.py` - 加减法生成器（一年级 10 以内）
- `consecutive_addition_subtraction.py` - 连加减生成器（一年级 10 以内）
- `currency_conversion.py` - 人民币换算生成器（元角分换算）

**生成器接口**：
```python
class TemplateGenerator(ABC):
    @abstractmethod
    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        """生成题目，返回结构化数据"""
        pass

    @abstractmethod
    def get_knowledge_points(self, template_config: dict) -> List[str]:
        """获取知识点列表"""
        pass
```

### 3.4 模型模块 (models/)

#### user.py
```python
class UserCreate(BaseModel)      # 注册请求
class UserLogin(BaseModel)       # 登录请求
class UserInDB(BaseModel)        # 数据库用户（含 grade 字段）
class UserGradeUpdate(BaseModel) # 年级更新请求（grade1~grade9）
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

#### question_template.py（2026-03 新增）
```python
class QuestionTemplate(BaseModel)        # 题目模板（含 generator_module 字段）
class QuestionTemplateListItem(BaseModel) # 模板列表项
class QuestionTemplateListResponse(BaseModel)
class TemplateGenerateRequest(BaseModel)  # 模板生成请求
class TemplateGenerateResponse(BaseModel) # 模板生成响应

# 支持的规则约束
SUPPORTED_RULES = {
    "ensure_different",    # 确保两个数不同
    "ensure_positive",     # 确保减法结果不为负数
    "ensure_divisible",    # 确保除法能整除
    "result_within_10",    # 确保结果 ≤ 10
    "result_within_20",    # 确保结果 ≤ 20
    "result_within_100",   # 确保结果 ≤ 100
}
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

### 4.1 数据库连接（重构后）

**重构前问题**: 每个文件重复定义 `DB_PATH`，违反 DRY 原则

```python
# 重构前 - 6 个文件都有重复代码
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"
DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"  # 路径混乱
```

**重构后 - 统一配置**:

```python
# config.py
BASE_DIR = Path(__file__).parent  # backend/ 目录
DB_PATH = BASE_DIR / "data" / "users.db"

# 任何需要数据库的文件
from config import DB_PATH

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 字典式访问
    return conn
```

**优势**:
- 单一职责：路径配置只在一个地方管理
- 易于维护：修改数据库位置只需改一处
- 不易出错：无需计算 `parent.parent.parent...`
- 代码清晰：导入即用，意图明确

### 4.2 初始化流程

```python
# db/__init__.py
def init_database():
    # 1. 创建 data 目录
    # 2. 连接数据库
    # 3. 执行 schema.sql
    # 4. 提交并关闭
```

### 4.3 迁移管理

```
db/migrations/
├── 001_add_questions_table.sql       # 题目表结构
└── 002_add_question_templates.sql    # 模板系统表（2026-03 新增）
```

**迁移脚本使用**:
```bash
cd backend
python -c "
import sqlite3
with open('db/migrations/002_add_question_templates.sql', 'r') as f:
    conn = sqlite3.connect('data/users.db')
    conn.executescript(f.read())
    conn.commit()
    conn.close()
"
```

### 4.4 模板系统数据库（2026-03 新增）

**question_templates** - 题目模板表：
```sql
CREATE TABLE question_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- 模板名称
    subject TEXT NOT NULL,        -- 学科：math/chinese/english
    grade TEXT NOT NULL,          -- 年级：grade1~grade9
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

**template_usage_logs** - 模板使用记录表：
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

### B. 重构说明

**数据库路径配置重构**:
- 问题：每个文件重复定义 `DB_PATH`，违反 DRY 原则
- 解决：在 `config.py` 统一配置，所有文件导入使用
- 代码减少：约 39 行

**服务层按领域分组**:
- 原结构：扁平 `services/` 目录
- 新结构：`services/ai/`, `services/user/`, `services/question/`, `services/admin/`
- 优势：同领域代码集中，便于导航和维护

**路由层重命名**:
- 原目录：`routers/`
- 新目录：`api/v1/`
- 优势：更清晰的 API 版本管理

**数据库目录重命名**:
- 原目录：`sql/`
- 新目录：`db/`
- 优势：更准确的语义

### C. 新增模块（2026-03）

**模板题目系统**:
- 新增 `services/template/` 模块
- 新增 `models/question_template.py` 模型
- 新增 `api/v1/templates.py` 路由
- 新增数据库迁移 `002_add_question_templates.sql`
- 新增生成器架构 `services/template/generators/`

**生成器架构特点**:
- 抽象基类 `TemplateGenerator`
- 每个模板对应独立生成器文件
- 注册表模式管理生成器
- 支持规则约束（ensure_positive, result_within_10 等）

### C. 相关文档
- [后端系统架构](./backend-system-architecture.md)
- [前后端交互逻辑](./frontend-backend-interaction-logic.md)
