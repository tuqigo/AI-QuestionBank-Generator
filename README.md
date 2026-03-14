# 题小宝 - AI 智能题库生成器

> 基于通义千问大模型，为 K12 学生生成个性化数学、语文、英语练习题

[![Python](https://img.shields.io/badge/Python-3.8-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 项目简介

**题小宝** 是一款面向小学生家长的 AI 智能题库生成器，支持：

- **多学科**: 数学、语文、英语
- **多年级**: 一年级至九年级 (grade1-9)
- **多题型**: 选择题、判断题、填空题、计算题、应用题、阅读理解、作文等
- **图片出题**: 上传题目图片，AI 识别后生成同类扩展题
- **历史记录**: 自动生成并保存出题记录，支持回看和分享
- **管理后台**: 管理员可查看用户数据、操作日志等

---

## 技术架构

### 后端

| 技术 | 说明 |
|------|------|
| **框架** | FastAPI 0.109+ |
| **AI API** | 通义千问 (DashScope) - `qwen-plus-latest` / `qwen-vl-plus` |
| **认证** | JWT (python-jose + bcrypt) |
| **邮件** | SMTP (163/Gmail/QQ 邮箱) |
| **数据库** | SQLite (用户数据、历史记录) |

### 前端

| 技术 | 说明 |
|------|------|
| **框架** | React 19 + TypeScript |
| **路由** | React Router v7 |
| **构建** | Vite 7 |
| **渲染** | marked (Markdown), MathJax (数学公式) |
| **部署** | Cloudflare Pages |

---

## 项目结构

```
AI-QuestionBank-Generator/
├── backend/
│   ├── main.py                    # FastAPI 入口，CORS 配置
│   ├── config.py                  # 环境变量配置，AI 提示词
│   ├── routers/
│   │   ├── auth.py                # 登录/注册/找回密码
│   │   ├── questions.py           # 题目生成 (提示词方式)
│   │   ├── questions_structured.py# 结构化题目生成 (JSON Schema)
│   │   ├── extend.py              # 图片扩展题
│   │   ├── history.py             # 历史记录查询/分享
│   │   └── admin.py               # 管理后台
│   ├── services/
│   │   ├── qwen_client.py         # 通义千问文本生成
│   │   ├── qwen_vision.py         # 通义千问视觉识别
│   │   ├── auth.py                # JWT 认证工具
│   │   ├── user_store.py          # 用户数据存储
│   │   ├── email_sender.py        # 邮件发送 (验证码)
│   │   └── ...
│   ├── models/
│   │   ├── user.py                # 用户数据模型
│   │   ├── question_record.py     # 题目记录模型
│   │   ├── otp.py                 # OTP 验证码模型
│   │   └── ...
│   ├── middleware/
│   │   └── jwt_auth.py            # JWT 中间件
│   ├── utils/
│   │   ├── logger.py              # 日志配置
│   │   ├── validators.py          # 参数校验
│   │   └── short_id.py            # 短 ID 生成
│   ├── .env.example               # 环境变量模板
│   └── requirements.txt           # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # 应用入口，路由配置
│   │   ├── MainContent.tsx        # 主界面 (出题/预览)
│   │   ├── LoginPage.tsx          # 登录/注册页面
│   │   ├── HistoryDetail.tsx      # 历史详情页
│   │   ├── SharePage.tsx          # 分享页
│   │   ├── StructuredPreview.tsx  # 结构化题目预览
│   │   ├── auth.ts                # Token 管理工具
│   │   └── main.tsx               # React 入口
│   ├── pages/
│   │   └── LandingPage.tsx        # 首页落地页
│   ├── admin/
│   │   └── App.tsx                # 管理后台
│   ├── package.json
│   └── vite.config.ts
├── document/                      # 项目文档
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+
- 通义千问 API Key ([申请地址](https://dashscope.console.aliyun.com/))

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

# 4. 部署到 Cloudflare Pages
npm run deploy
```

访问 `http://localhost:5173` 使用应用。

---

## API 接口

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
| `/api/questions/generate` | POST | 是 | 根据提示词生成题目 |
| `/api/questions/generate-structured` | POST | 是 | 结构化 JSON 方式生成题目 |
| `/api/questions/extend-from-image` | POST | 是 | 上传图片生成扩展题 |

### 历史记录接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/history` | GET | 是 | 获取历史记录列表 |
| `/api/history/{id}` | GET | 是 | 获取单条记录详情 |
| `/api/history/{id}/questions` | GET | 是 | 获取试卷题目详情（含作答行数） |
| `/api/history/{id}/answers` | GET | 是 | 获取整卷答案 |
| `/api/history/{id}/share` | POST | 是 | 生成分享链接 |
| `/api/history/{id}/copy` | POST | 是 | 复制记录 (运营功能) |

### 分享页接口（无需登录）

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/share/history/{id}` | GET | 否 | 通过分享链接获取记录 |
| `/api/share/history/{id}/questions` | GET | 否 | 分享页获取试卷题目 |
| `/api/share/history/{id}/answers` | GET | 否 | 分享页获取整卷答案 |

### 管理后台接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/admin/stats` | GET | 管理员 | 获取统计数据 |
| `/api/admin/users` | GET | 管理员 | 用户列表 |
| `/api/admin/records` | GET | 管理员 | 题目记录列表 |
| `/api/admin/logs` | GET | 管理员 | 操作日志列表 |

---

## 环境变量

### 后端配置 (.env)

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

### 核心表结构

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `users` | 用户表 | id, email, password_hash, created_at |
| `user_question_records` | 试卷表 | id, short_id, user_id, title, ai_response |
| `questions` | 题目表 | id, short_id, record_id, type, stem, options, answer_blanks, rows_to_answer, answer_text |
| `otps` | 验证码表 | id, email, code, expire_at |
| `admin_logs` | 管理日志表 | id, admin_id, action, details |

### 表关系

```
users (用户表)
  └── 一对多 → user_question_records (试卷表)
       └── 一对多 → questions (题目表)
```

### questions 表字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER | 主键 |
| `short_id` | TEXT | 短 ID（用于 URL） |
| `record_id` | INTEGER | 所属试卷 ID |
| `question_index` | INTEGER | 题号 |
| `type` | TEXT | 题型（SINGLE_CHOICE 等） |
| `stem` | TEXT | 题干 |
| `options` | TEXT | 选项 JSON（选择题用） |
| `passage` | TEXT | 阅读材料 JSON（阅读理解用） |
| `sub_questions` | TEXT | 子题 JSON（阅读理解/完形填空用） |
| `knowledge_points` | TEXT | 知识点 JSON |
| `answer_blanks` | INTEGER | 填空题空格数 |
| `rows_to_answer` | INTEGER | 预留作答行数 |
| `answer_text` | TEXT | 参考答案 |

---

## 核心功能说明

### 1. 题目生成

支持两种出题方式：

**方式一：提示词生成**
```
POST /api/questions/generate
{
  "prompt": "生成三年级数学加减法练习题 10 道"
}
```

**方式二：结构化生成 (JSON Schema)**
```
POST /api/questions/generate-structured
{
  "subject": "math",
  "grade": "grade3",
  "questionTypes": ["SINGLE_CHOICE", "CALCULATION"],
  "count": 10
}
```

### 2. 图片扩展题

上传图片后，AI 识别题目内容并生成同类扩展题：

```
POST /api/questions/extend-from-image
Content-Type: multipart/form-data

image: <file>
count: 5  # 扩展题数量
```

### 3. 用户认证

- 邮箱 + 验证码注册
- 邮箱 + 密码登录
- 邮箱验证码重置密码
- JWT Token 认证

### 4. 历史记录

- 自动生成并保存出题记录
- 支持按时间排序、分页查询
- 生成分享链接 (公开访问)
- 运营人员可复制记录到目标用户

---

## 题型说明

### 通用题型 (全学科适用)

| 题型 | 代码 | 说明 |
|------|------|------|
| 单选题 | `SINGLE_CHOICE` | 4 个选项，选 1 个 |
| 多选题 | `MULTIPLE_CHOICE` | 多个选项，选多个 |
| 判断题 | `TRUE_FALSE` | 对/错 |
| 填空题 | `FILL_BLANK` | 挖空填答案 |

### 数学专属题型

| 题型 | 代码 | 说明 |
|------|------|------|
| 计算题 | `CALCULATION` | 计算/解方程 |
| 应用题 | `WORD_PROBLEM` | 实际应用题 |

### 语文/英语专属题型

| 题型 | 代码 | 说明 |
|------|------|------|
| 阅读理解 | `READ_COMP` | 阅读材料 + 子题目 |
| 作文 | `ESSAY` | 书面表达 |

### 英语专属题型

| 题型 | 代码 | 说明 |
|------|------|------|
| 完形填空 | `CLOZE` | 完形填空 |

---

## 前端架构

### 双模式渲染

前端采用双模式渲染架构，支持屏幕显示和打印输出两种模式：

| 模式 | 说明 | 特点 |
|------|------|------|
| **渲染模式** (`render`) | 浏览器屏幕预览 | 背景色、圆角边框、大间距 |
| **打印模式** (`print`) | 打印/PDF 导出 | 紧凑布局、无背景色、适合打印 |

### 核心组件

- **QuestionRenderer**: 题目渲染入口组件
- **StructuredPreviewShared**: 预览/分享通用组件
- **题目组件**: 11 种题型组件，均支持双模式切换

### 打印功能

- 使用 `printUtils.ts` 中的 `handlePrint()` 函数
- 支持结构化题目数据打印
- MathJax 公式渲染支持
- CSS @media print 样式分离

---

## 开发指南

### 添加新的 API 路由

1. 在 `backend/routers/` 创建新的路由文件
2. 在 `backend/main.py` 中注册路由
3. 添加 API 文档注释

### 添加新的题型

1. 在 `config.py` 的 `QUESTION_SYSTEM_PROMPT` 中添加题型定义
2. 更新 JSON Schema 校验规则
3. 前端添加对应的渲染组件

### 部署

#### 后端部署

```bash
# 使用 Gunicorn + Uvicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端部署

前端已配置 Cloudflare Pages 自动部署：

```bash
npm run deploy
```

---

## 常见问题

### 1. 题目生成失败

- 检查 `DASHSCOPE_API_KEY` 是否正确
- 检查网络连接 (需要访问阿里云 API)
- 查看 `backend/logs/` 日志文件

### 2. 验证码发送失败

- 检查 SMTP 配置是否正确
- 确认邮箱授权码 (非登录密码)
- 检查防火墙是否放行 SMTP 端口

### 3. 跨域错误

- 检查 `.env` 中的 `ALLOW_ORIGINS` 配置
- 确保前端地址在允许列表中

---

## 许可证

MIT License

---

## 致谢

- [通义千问](https://dashscope.console.aliyun.com/) - AI 模型支持
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [React](https://react.dev/) - 前端框架
- [Vite](https://vite.dev/) - 构建工具

---

*最后更新：2026-03-14*
