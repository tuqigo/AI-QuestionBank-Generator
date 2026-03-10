# 项目概述

**小学生 AI 题库生成器** - 为学生家长老师生成数学、语文等学科练习题的 Web 应用。

## 技术栈

### 后端
- **框架**: FastAPI  python版本3.8
- **AI API**: 通义千问 (DashScope) - `qwen-plus-latest` / `qwen-vl-plus`
- **认证**: JWT (python-jose + bcrypt)
- **包管理**: pip + requirements.txt

### 前端
- **框架**: React 19 + TypeScript
- **构建工具**: Vite 7
- **核心依赖**:
  - `marked` - Markdown 渲染
  - `html2pdf.js` - PDF 导出
- **包管理**: npm
- **前端页面设计准则**: 遵循frontend-design 准则，frontend-design为我安装的plugin

## 项目结构

```
zuoyebang/
├── backend/
│   ├── main.py              # FastAPI 入口，CORS 配置
│   ├── config.py            # 环境变量配置
│   ├── routers/
│   │   ├── auth.py          # 登录/注册接口
│   │   ├── questions.py     # 题目生成接口
│   │   └── extend.py        # 图片扩展题接口
│   ├── services/
│   │   ├── qwen_client.py   # 通义千问文本生成
│   │   ├── qwen_vision.py   # 通义千问视觉识别
│   │   ├── auth.py          # JWT 认证
│   │   └── user_store.py    # 用户数据存储
│   ├── models/
│   │   └── user.py          # 用户数据模型
│   └── utils/
│       └── logger.py        # 日志配置
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # 应用入口，认证逻辑
│   │   ├── MainContent.tsx  # 主界面（题目生成/预览）
│   │   ├── LoginPage.tsx    # 登录/注册页面
│   │   ├── auth.ts          # Token 管理工具
│   │   ├── types.ts         # TypeScript 类型定义
│   │   └── main.tsx         # React 入口
│   └── package.json
└── README.md
```

## 开发命令

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev        # 开发模式
npm run build      # 生产构建
```

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`：

```
DASHSCOPE_API_KEY=sk-your-api-key
QWEN_MODEL=qwen-plus-latest
QWEN_VISION_MODEL=qwen-vl-plus
JWT_SECRET=your-random-secret
```

## API 接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/auth/register` | POST | 否 | 用户注册 |
| `/api/auth/login` | POST | 否 | 用户登录 |
| `/api/auth/me` | GET | 是 | 获取当前用户 |
| `/api/questions/generate` | POST | 是 | 根据提示词生成题目 |
| `/api/questions/extend-from-image` | POST | 是 | 上传图片生成扩展题 |

## 核心业务逻辑

### 题目生成 Prompt 规则 (qwen_client.py)
- 默认年级：一年级（若用户未指定）
- 默认数量：15 道题
- 输出格式：Markdown，题号用 `1.` `2.` 格式
- 选择题选项：`A.` `B.` `C.` `D.` 每行一个
- 填空题：使用 `______` (至少 6 个下划线) 或 `[  ]` (3 个空格)
- 比较大小：`13 [ ] 17` 或 `13 ____ 17`
- 答案页：用 `<!-- PAGE_BREAK -->` 分隔，便于 PDF 分页

## 代码风格约定

- **Python**: 遵循 PEP 8，使用 f-string，类型注解
- **TypeScript/React**: 函数组件 + Hooks，箭头函数
- **命名**:
  - Python - snake_case
  - TypeScript - camelCase/PascalCase

## 重要 python版本3.8

