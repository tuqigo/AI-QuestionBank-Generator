# 开发指南

> 题小宝 AI 题库生成器 - 完整开发文档

最后更新：2026-03-14

---

## 目录

1. [快速开始](#快速开始)
2. [环境配置](#环境配置)
3. [数据库设计](#数据库设计)
4. [API 接口文档](#api 接口文档)
5. [前端架构](#前端架构)
6. [题目与答案分离改造](#题目与答案分离改造)
7. [常见问题](#常见问题)

---

## 快速开始

### 后端启动

```bash
cd backend

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 DASHSCOPE_API_KEY 等配置

# 3. 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看 API 文档。

### 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务
npm run dev

# 3. 生产构建
npm run build
```

访问 `http://localhost:5173` 使用应用。

---

## 环境配置

### 后端环境变量 (.env)

| 变量 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `DASHSCOPE_API_KEY` | 是 | 通义千问 API Key | - |
| `QWEN_MODEL` | 否 | 文本生成模型 | `qwen-plus-latest` |
| `QWEN_VISION_MODEL` | 否 | 视觉识别模型 | `qwen-vl-plus` |
| `JWT_SECRET` | 是 | JWT 密钥 | `change-me-in-production` |
| `JWT_EXPIRE_MINUTES` | 否 | Token 有效期 (分钟) | `10080` (7 天) |
| `ALLOW_ORIGINS` | 否 | CORS 允许来源 | `http://localhost:5173` |
| `SMTP_HOST` | 否 | SMTP 服务器 | `smtp.163.com` |
| `SMTP_PORT` | 否 | SMTP 端口 | `465` |
| `SMTP_USER` | 否 | SMTP 用户名 | - |
| `SMTP_PASS` | 否 | SMTP 密码/授权码 | - |
| `SMTP_FROM_NAME` | 否 | 发件人名称 | `题小宝` |
| `SMTP_USE_TLS` | 否 | 使用 TLS | `true` |
| `OTP_EXPIRE_MINUTES` | 否 | 验证码有效期 (分钟) | `5` |
| `ADMIN_PASSWORD` | 否 | 管理员密码 | `admin123` |
| `TARGET_USER_IDS` | 否 | 运营目标用户 ID 列表 | - |

---

## 数据库设计

### 表结构概览

```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP
);

-- 试卷表
CREATE TABLE user_question_records (
    id INTEGER PRIMARY KEY,
    short_id TEXT UNIQUE,
    user_id INTEGER,
    title TEXT,
    prompt_type TEXT,
    prompt_content TEXT,
    ai_response TEXT,  -- 原始 AI 响应 JSON
    created_at TIMESTAMP
);

-- 题目表（2026-03-14 新增）
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    short_id TEXT UNIQUE,
    record_id INTEGER,           -- 所属试卷 ID
    question_index INTEGER,      -- 题号
    type TEXT,                   -- 题型
    stem TEXT,                   -- 题干
    options TEXT,                -- 选项 JSON
    passage TEXT,                -- 阅读材料 JSON
    sub_questions TEXT,          -- 子题 JSON
    knowledge_points TEXT,       -- 知识点 JSON
    answer_blanks INTEGER,       -- 填空题空格数
    rows_to_answer INTEGER,      -- 作答行数
    answer_text TEXT,            -- 答案
    created_at TIMESTAMP
);
```

### 作答行数计算规则

| 题型 | 行数 | 说明 |
|------|------|------|
| SINGLE_CHOICE | 1 | 单选题 |
| MULTIPLE_CHOICE | 1 | 多选题 |
| TRUE_FALSE | 1 | 判断题 |
| FILL_BLANK | 1 | 填空题 |
| CALCULATION | 3 | 计算题 |
| WORD_PROBLEM | 3 | 应用题 |
| GEOMETRY | 3 | 几何题 |
| POETRY_APP | 3 | 古诗文鉴赏 |
| ESSAY | 10 | 作文题 |
| READ_COMP | passage 行数 + 子题数×2 | 阅读理解 |
| CLOZE | passage 行数 + 子题数×2 | 完形填空 |

---

## API 接口文档

### 认证接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/send-otp` | POST | 否 | 发送邮箱验证码 |
| `/api/auth/register` | POST | 否 | 用户注册 |
| `/api/auth/login` | POST | 否 | 用户登录 |
| `/api/auth/reset-password` | POST | 否 | 重置密码 |
| `/api/auth/me` | GET | 是 | 获取当前用户 |
| `/api/auth/logout` | POST | 是 | 登出 |

### 题目生成接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/questions/generate` | POST | 是 | 提示词方式生成题目 |
| `/api/questions/structured` | POST | 是 | 结构化 JSON 方式生成题目 |
| `/api/questions/extend-from-image` | POST | 是 | 上传图片生成扩展题 |

### 历史记录接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/history` | GET | 是 | 获取历史记录列表（游标分页） |
| `/api/history/{shortId}` | GET | 是 | 获取单条记录详情 |
| `/api/history/{shortId}/questions` | GET | 是 | 获取试卷题目详情 |
| `/api/history/{shortId}/answers` | GET | 是 | 获取整卷答案 |
| `/api/history/{shortId}/share` | POST | 是 | 生成分享链接 |
| `/api/history/{shortId}` | DELETE | 是 | 删除历史记录 |

### 分享页接口（无需登录）

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/share/history/{shortId}` | GET | 否 | 获取分享记录 |
| `/api/share/history/{shortId}/questions` | GET | 否 | 获取分享题目 |
| `/api/share/history/{shortId}/answers` | GET | 否 | 获取分享答案 |

---

## 前端架构

### 目录结构

```
frontend/src/
├── App.tsx                    # 应用入口，路由配置
├── MainContent.tsx            # 主界面（出题/预览）
├── LoginPage.tsx              # 登录/注册页面
├── HistoryDetail.tsx          # 历史详情页
├── SharePage.tsx              # 分享页
├── StructuredPreview.tsx      # 结构化题目预览页
├── auth.ts                    # Token 管理工具
├── main.tsx                   # React 入口
├── api/
│   └── history.ts             # 历史记录相关 API
├── components/
│   ├── QuestionRenderer.tsx   # 题目渲染主组件
│   ├── StructuredPreviewShared.tsx  # 预览/分享通用组件
│   └── questions/             # 题型组件
│       ├── SingleChoice.tsx
│       ├── MultipleChoice.tsx
│       ├── TrueFalse.tsx
│       ├── FillBlank.tsx
│       ├── Calculation.tsx
│       ├── WordProblem.tsx
│       ├── ReadComp.tsx
│       ├── Cloze.tsx
│       └── Essay.tsx
├── config/                    # 配置文件
├── styles/                    # 全局样式
├── utils/
│   ├── printUtils.ts          # 打印工具
│   ├── markdownProcessor.ts   # Markdown 渲染
│   └── promptValidator.ts     # 提示词校验
└── types/
    ├── structured.ts          # 结构化题目类型定义
    └── index.ts               # 通用类型定义
```

### 题目渲染流程

```
用户请求生成题目
    ↓
后端返回 StructuredGenerateResponse
    ↓
前端保存 short_id
    ↓
QuestionRenderer 根据 type 渲染对应组件
    ↓
StructuredPreviewShared 统一渲染 MathJax
    ↓
用户点击打印 → printUtils.handlePrint()
```

### 双模式渲染

| 模式 | 说明 | 特点 |
|------|------|------|
| render | 屏幕预览 | 背景色、圆角、大间距 |
| print | 打印输出 | 紧凑布局、无背景色 |

---

## 题目与答案分离改造

### 改造背景

**改造日期**: 2026-03-14

原有系统的问题：
1. 题目数据存储在 `user_question_records.ai_response` 中，为原始 JSON 字符串
2. 缺少后端处理的辅助字段（`rows_to_answer`、`answer_blanks`）
3. 无法单独查询题目答案
4. 历史记录详情页无法获取结构化题目数据

### 改造内容

#### 后端改造

1. **新增 questions 表** - 独立存储题目数据
2. **新增服务**:
   - `services/question_data_cleaner.py` - 数据清洗服务
   - `services/question_store.py` - 题目存储服务
3. **新增 API**:
   - `GET /api/history/{shortId}/questions` - 获取题目详情
   - `GET /api/history/{shortId}/answers` - 获取答案
   - `GET /api/share/history/{shortId}/questions` - 分享页题目
   - `GET /api/share/history/{shortId}/answers` - 分享页答案

#### 前端改造

1. **类型定义更新** - `StructuredQuestion` 添加 `answer_blanks`、`answer_text` 字段
2. **API 函数新增** - `getHistoryQuestions()`、`getHistoryAnswers()` 等
3. **组件改造**:
   - `HistoryDetail.tsx` - 调用新接口，添加查看答案功能
   - `StructuredPreview.tsx` - 保存 short_id，添加查看答案功能

### 数据流程

```
AI 生成题目
    ↓
保存 ai_response → user_question_records
    ↓
QuestionDataCleaner 解析 JSON
    ↓
计算 rows_to_answer、answer_blanks
    ↓
批量插入 → questions 表
    ↓
前端查询 questions 表获取结构化数据
```

### 文件变更

#### 后端
- **新增**:
  - `sql/migrations/001_add_questions_table.sql`
  - `services/question_data_cleaner.py`
  - `services/question_store.py`
  - `test_question_cleaner.py`
- **修改**:
  - `sql/schema.sql`
  - `routers/history.py`
  - `routers/questions_structured.py`

#### 前端
- **修改**:
  - `src/types/structured.ts`
  - `src/api/history.ts`
  - `src/HistoryDetail.tsx`
  - `src/HistoryDetail.css`
  - `src/StructuredPreview.tsx`
  - `src/StructuredPreview.css`
  - `src/SharePage.tsx`

---

## 常见问题

### 题目生成失败

**可能原因**:
1. `DASHSCOPE_API_KEY` 配置错误
2. 网络连接问题（需访问阿里云 API）
3. AI 服务超时

**解决方法**:
1. 检查 `.env` 中的 API Key 是否正确
2. 查看 `backend/logs/` 日志文件
3. 减少题目数量或简化提示词

### 验证码发送失败

**可能原因**:
1. SMTP 配置错误
2. 邮箱授权码填写错误（非登录密码）
3. 防火墙阻止 SMTP 端口

**解决方法**:
1. 检查 SMTP_HOST、SMTP_PORT 配置
2. 使用邮箱服务商提供的授权码
3. 确认 465/587 端口未被阻止

### 跨域错误

**现象**: 前端请求后端时报 CORS 错误

**解决方法**:
1. 检查 `.env` 中的 `ALLOW_ORIGINS` 配置
2. 确保前端地址在允许列表中
3. 生产环境配置正确的域名

### React 接口重复调用

**现象**: 开发模式下 useEffect 执行两次

**解决方法**:
```typescript
const hasLoadedRef = useRef(false)

useEffect(() => {
  if (!id || hasLoadedRef.current) return
  hasLoadedRef.current = true
  // API 调用
}, [id])
```

这是 React Strict Mode 的正常行为，用于检测副作用。使用 ref 跟踪加载状态可避免重复调用。

---

## 开发命令参考

### 后端

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务
uvicorn main:app --reload

# 运行测试
python test_question_cleaner.py

# 数据库迁移
python -c "import sqlite3; conn=sqlite3.connect('data/users.db'); conn.executescript(open('sql/migrations/001_add_questions_table.sql').read())"
```

### 前端

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 部署到 Cloudflare Pages
npm run deploy
```

---

*本文档由开发团队维护，如有问题请联系技术支持。*
