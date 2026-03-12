# 题小宝

为中小学 1-6 年级家长生成数学、语文等学科练习题，支持 AI 出题、PDF 下载与打印。

## 功能

- **提示词生成**：输入需求（如「小学一年级 10 以内加减法 20 道，带答案」）生成题目
- **图片扩展题**：上传题目图片，AI 识别后生成同类型扩展题
- **常用题型快捷按钮**：口算题、填空题、应用题、选择题、阅读理解
- **HTML 预览**：实时渲染 Markdown 题目
- **PDF 下载**：导出为 PDF，答案单独一页
- **打印**：支持浏览器打印
- **用户登录**：注册/登录，多用户区分

## 技术栈

- 后端：FastAPI + 通义千问 API (DashScope)
- 前端：React + Vite + TypeScript
- 认证：JWT

## 快速开始

### 1. 配置环境变量

复制 `backend/.env.example` 为 `backend/.env`，填入：

```
DASHSCOPE_API_KEY=sk-your-api-key
QWEN_MODEL=qwen-plus
QWEN_VISION_MODEL=qwen-vl-plus
JWT_SECRET=your-random-secret
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 4. 使用流程

1. 注册/登录
2. 输入提示词或点击快捷按钮
3. 点击「生成题目」
4. 预览后点击「下载 PDF」或「打印」

## 项目结构

```
zuoyebang/
├── backend/
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # 配置
│   ├── routers/          # 路由：auth, questions, extend
│   ├── services/         # 业务：qwen_client, qwen_vision, auth, user_store
│   └── models/           # 数据模型
├── frontend/
│   └── src/
│       ├── App.tsx       # 应用入口与登录逻辑
│       ├── MainContent.tsx  # 主界面
│       ├── LoginPage.tsx # 登录/注册
│       └── auth.ts       # Token 管理
└── README.md
```

## API 说明

- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取当前用户（需 Token）
- `POST /api/questions/generate` - 根据提示词生成题目（需 Token）
- `POST /api/questions/extend-from-image` - 上传图片生成扩展题（需 Token）

uvicorn main:app --reload --port 8000



nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &