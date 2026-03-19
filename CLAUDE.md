# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作提供指导。

## 项目概述

**题小宝 (TiXiaoBao)** - AI 驱动的题库生成器，面向 K12 教育（1-9 年级）。使用 AI（DashScope/Qwen）和基于规则的系统生成数学、语文和英语练习题。

## 快速开始

### 后端 (FastAPI + SQLite)

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 在 .env 中配置 DASHSCOPE_API_KEY、JWT_SECRET 等

# 运行数据库迁移
python -m db.migrations_cli migrate

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端 (React 19 + Vite)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生产环境构建
npm run build

# 部署到 Cloudflare Pages
npm run deploy
```

## 架构

### 后端结构 (`backend/`)

```
backend/
├── main.py                 # FastAPI 应用入口
├── config.py               # 统一配置（DB_PATH、JWT、API 密钥）
├── api/v1/                 # API 路由
│   ├── auth.py            # 用户认证（OTP + JWT）
│   ├── questions.py       # AI 题目生成
│   ├── questions_structured.py  # 结构化 JSON 生成
│   ├── history.py         # 用户历史 + 分享
│   ├── templates.py       # 基于模板的生成
│   └── admin.py           # 管理员操作
├── services/               # 业务逻辑层
│   ├── ai/                # Qwen 客户端、视觉识别、数据清洗
│   ├── user/              # 用户服务 + 存储
│   ├── question/          # 题目服务 + 存储
│   ├── admin/             # 管理员认证 + 操作日志
│   └── template/          # 模板系统 + 生成器
├── db/
│   ├── schema.sql         # 完整数据库架构
│   └── migrations/        # 增量迁移脚本
└── data/                  # SQLite 数据库 (tixiaobao.db)
```

### 前端结构 (`frontend/`)

```
frontend/
├── src/
│   ├── App.tsx            # 主应用（含 React Router）
│   ├── features/          # 功能模块
│   │   ├── question-generator/
│   │   ├── history/
│   │   └── auth/
│   ├── components/
│   │   ├── questions/     # 题目类型组件
│   │   └── shared/        # 可复用 UI 组件
│   ├── hooks/             # 自定义 hooks（useMathJax, useToast）
│   ├── api/               # API 客户端模块
│   └── utils/             # 工具函数（printUtils, markdownProcessor）
└── public/
```

## 核心技术栈

| 层级 | 技术 |
|-------|------------|
| 后端 | FastAPI (Python 3.8+ 写后端代码要兼容), SQLite, JWT |
| 前端 | React 19, TypeScript, Vite 7 |
| AI | DashScope (Qwen-plus, Qwen-vision) |
| 渲染 | MathJax (LaTeX), marked (Markdown) |
| 部署 | Cloudflare Pages (前端), uvicorn (后端) |

## 核心功能

### 1. AI 题目生成
- **端点**: `POST /api/questions/structured`
- 使用 Batch 系统高效调用 API（10 请求/批，3 秒超时）
- 支持文本提示和图片上传（视觉识别）
- 返回包含 meta + questions 数组的结构化 JSON

### 2. 基于模板的生成
- **端点**: `POST /api/templates/generate`
- 基于规则的生成器（无 AI 成本，即时响应）
- `services/template/generators/` 中的生成器注册模式
- 已实现：数字比较、加减法、连加连减、货币转换

### 3. 认证系统
- OTP 邮箱验证（5 分钟过期，5 次尝试限制，速率限制）
- JWT Token（用户 7 天，管理员 2 小时）
- 新用户必须选择年级


## 部署

### 后端（生产环境）
```bash
# 使用重启脚本（包含版本检查、迁移、健康检查）
./restart_backend.sh
```

### 前端（Cloudflare Pages）

**注意**：在中国大陆部署时需要配置代理，否则可能遇到连接问题。

```bash
cd frontend

# 配置代理（中国大陆地区必需）
export HTTPS_PROXY="http://127.0.0.1:10808"
```

#### 部署方式

**方式一：使用 deploy 脚本**
```bash
npm run deploy
```

**方式二：wrangler 部署（绕过 UTF-8 bug，推荐）**
```bash
npx wrangler pages deploy dist \
  --project-name=zyb-frontend \
  --branch=main \
  --commit-hash=$(git rev-parse HEAD) \
  --commit-message="redeploy"
```

**git push 也需要代理**：
```bash
export HTTPS_PROXY="http://127.0.0.1:10808"
git push origin main
```

## 环境变量

### 必需配置 (.env)
```bash
DASHSCOPE_API_KEY=sk-xxx          # 无默认值
JWT_SECRET=your-random-secret     # 无默认值，使用 secrets.token_urlsafe(32)
ADMIN_PASSWORD_HASH=$2b$12$...    # bcrypt 哈希

SMTP_HOST=smtp.163.com
SMTP_USER=your-email@163.com
SMTP_PASS=your-auth-code
```

完整列表见 `.env.example`。

## 数据库操作规范
```
数据库的设计要遵循 ：禁止数据库外键、改用业务层保证
操作语句撰写
1.DDL在schema.sql 
2.DML 在migrations文件夹下面
操作语句执行
1.DDL启动时自动执行 
2.DML 通过命令   python -m db.migrations_cli migrate 执行
```

## 数据库迁移

```bash
# 检查状态
python -m db.migrations_cli status

# 运行待处理迁移
python -m db.migrations_cli migrate

# 查看历史
python -m db.migrations_cli history
```

迁移脚本存储在 `db/migrations/`，并在 `schema_migrations` 表中跟踪。

## 代码风格与规范

- **后端**: PEP 8，鼓励使用类型提示
- **前端**: TypeScript 严格模式，使用 Hooks 的函数式组件
- **提交**: Conventional Commits 格式（`feat:`, `fix:`, `refactor:`, 等）

## 常见任务

### 添加新的题目类型生成器
1. 在 `backend/services/template/generators/` 中创建生成器类
2. 继承 `TemplateGenerator` 基类
3. 在 `generators/__init__.py` 中注册
4. 添加模板配置的迁移

### 添加新的题型组件
1. 在 `frontend/src/components/questions/` 中创建组件
2. 遵循 `QuestionRendererProps` 接口
3. 在 `QuestionRenderer.tsx` 中注册

### 调试 AI 生成问题
1. 检查 `backend/logs/` 中的 API 日志
2. 验证 `.env` 中的 `DASHSCOPE_API_KEY`
3. 检查 `ai_generation_records` 表中的错误消息


### 重要说明
1. 不要轻易push以及部署代码，除非收到我明确指令，我让你提交代码，你只需要commit无需push
2. **Web Search 代理配置**：当需要访问外网（如 GitHub、Google 搜索等）时，必须使用以下代理配置：
   ```bash
   HTTPS_PROXY="http://127.0.0.1:10808"
   ```
