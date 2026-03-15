# 前端代码结构文档

## 1. 项目概述

### 1.1 基本信息

- **项目名称**: 题小宝 - 小学生 AI 题库生成器（前端）
- **技术栈**: React 19 + TypeScript + Vite 7
- **包管理器**: npm

### 1.2 快速开始

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

## 2. 目录结构

### 2.1 完整目录树

```
frontend/
├── public/                     # 静态资源目录
│   ├── icon64.svg             # 应用图标
│   └── ...
├── src/                        # 源代码目录
│   ├── admin/                 # 管理后台模块
│   │   ├── pages/             # 管理页面
│   │   │   ├── LoginPage.tsx  # 管理员登录
│   │   │   ├── UsersPage.tsx  # 用户管理
│   │   │   ├── OperationLogsPage.tsx  # 操作日志
│   │   │   ├── AiRecordsPage.tsx      # AI 生成记录
│   │   │   ├── AiRecordDetailPage.tsx # AI 记录详情
│   │   │   ├── UserDetailPage.tsx     # 用户详情
│   │   │   └── UserRecordDetailPage.tsx # 用户记录详情
│   │   ├── services/
│   │   │   └── api.ts         # 管理后台 API 客户端
│   │   ├── App.tsx            # 管理后台入口组件
│   │   └── auth.ts            # 管理员认证工具
│   │
│   ├── components/            # 通用组件目录
│   │   ├── questions/         # 题型组件
│   │   │   ├── SingleChoice.tsx    # 单选题
│   │   │   ├── MultipleChoice.tsx  # 多选题
│   │   │   ├── TrueFalse.tsx       # 判断题
│   │   │   ├── FillBlank.tsx       # 填空题
│   │   │   ├── Calculation.tsx     # 计算题
│   │   │   ├── WordProblem.tsx     # 应用题
│   │   │   ├── ReadComp.tsx        # 阅读理解
│   │   │   ├── Cloze.tsx           # 完形填空
│   │   │   └── Essay.tsx           # 作文题
│   │   ├── shared/            # 通用 UI 组件
│   │   │   ├── Button.tsx     # 按钮组件
│   │   │   ├── LoadingSpinner.tsx # 加载动画
│   │   │   ├── Modal.tsx      # 模态框
│   │   │   └── index.ts       # 统一导出
│   │   ├── QuestionRenderer.tsx    # 题目渲染器（路由分发）
│   │   ├── StructuredPreviewShared.tsx  # 结构化预览共享组件
│   │   └── GradeSelectorModal.tsx   # 年级选择器弹窗（新增）
│   │
│   ├── config/                # 配置文件
│   │   └── questionConfig.ts  # 题目配置常量
│   │
│   ├── core/                  # 核心模块
│   │   ├── api/               # API 客户端
│   │   │   └── history.ts     # 历史记录 API
│   │   └── auth/              # 认证模块
│   │       ├── authFactory.ts # 认证工厂（工厂模式）
│   │       ├── userAuth.ts    # C 端用户认证
│   │       └── adminAuth.ts   # 管理员认证
│   │
│   ├── features/              # 功能模块（按业务领域组织）
│   │   ├── auth/              # 认证功能
│   │   │   ├── LoginPage.tsx  # 登录页
│   │   │   └── LoginModal.tsx # 登录弹窗
│   │   ├── question-generator/# 题目生成
│   │   │   ├── MainContent.tsx      # 主界面
│   │   │   ├── MainContent.css      # 主界面样式（模块化导入）
│   │   │   ├── header.css           # 头部样式
│   │   │   │   sidebar.css          # 侧边栏样式
│   │   │   │   preview.css          # 预览区样式
│   │   │   │   modals.css           # 弹窗样式
│   │   │   ├── StructuredPreview.tsx# 结构化预览
│   │   │   └── ProgressModal.tsx    # 进度弹窗
│   │   ├── history/           # 历史记录
│   │   │   ├── HistoryList.tsx      # 历史列表
│   │   │   ├── HistoryDetail.tsx    # 历史详情
│   │   │   └── SharePage.tsx        # 分享页
│   │   └── landing/           # 落地页
│   │       └── LandingPage.tsx
│   │
│   ├── hooks/                 # 自定义 Hooks
│   │   ├── useMathJax.ts      # MathJax 渲染 Hook
│   │   └── index.ts           # 统一导出
│   │
│   ├── types/                 # 类型定义
│   │   ├── index.ts           # 通用类型（历史记录等）
│   │   ├── question.ts        # 题目相关类型
│   │   ├── mathjax.ts         # MathJax 全局类型
│   │   └── structured.ts      # 结构化数据类型
│   │
│   ├── utils/                 # 工具函数
│   │   ├── promptValidator.ts # 提示词校验
│   │   ├── markdownProcessor.ts# Markdown 处理
│   │   └── printUtils.ts      # 打印导出
│   │
│   ├── App.tsx                # 应用入口组件
│   ├── main.tsx               # React 入口文件
│   └── global.d.ts            # 全局类型声明（引用 types/mathjax）
│
├── index.html                 # HTML 入口（含 MathJax 预配置）
├── package.json               # 项目配置
├── tsconfig.json              # TypeScript 配置
├── vite.config.ts             # Vite 配置
└── wrangler.toml              # Cloudflare Workers 配置
```

### 2.2 目录组织原则

#### 按功能特性组织 (Feature-based)

```
src/
├── features/       # 业务功能模块
│   ├── auth/       # 认证相关
│   ├── question-generator/  # 题目生成
│   └── history/    # 历史记录
```

**优点**:
- 高内聚：相关代码集中在一起
- 易于理解：新人可以快速定位功能代码
- 易于删除：不需要的功能可以整块删除

#### 核心模块分离

```
src/
├── core/           # 核心基础设施
│   ├── api/        # API 客户端
│   └── auth/       # 认证服务
├── components/     # 通用 UI 组件
├── config/         # 配置文件
└── utils/          # 工具函数
```

---

## 3. 核心模块说明

### 3.1 入口文件

#### main.tsx
```typescript
// React 应用入口
// 创建 root 并挂载 App 组件
```

#### App.tsx
```typescript
// 主应用组件
// - 路由配置 (React Router)
// - 用户认证状态管理
// - 路由守卫逻辑
```

### 3.2 核心模块 (core/)

#### core/auth/authFactory.ts
认证工厂模块 - 使用工厂模式减少代码重复：

| 函数 | 说明 |
|------|------|
| `createAuthStorage(key)` | 创建认证存储实例（token 管理） |
| `createFetchWithAuth(auth, timeout, on401)` | 创建带认证的 fetch 包装器 |

**优势**:
- 统一错误处理（try-catch）
- 统一的 401 响应处理逻辑
- 支持可配置的超时时间

#### core/auth/userAuth.ts
C 端用户认证工具函数（使用工厂模式）：

| 函数 | 说明 |
|------|------|
| `getToken()` | 从 localStorage 获取 token |
| `setToken(token)` | 存储 token |
| `clearToken()` | 清除 token |
| `fetchWithAuth(url, options)` | 带认证的 fetch（120s 超时，自动 401 处理） |

#### core/auth/adminAuth.ts
管理后台认证工具函数（使用工厂模式）：

| 函数 | 说明 |
|------|------|
| `getAdminToken()` | 从 localStorage 获取 admin token |
| `setAdminToken(token)` | 存储 admin token |
| `clearAdminToken()` | 清除 admin token |
| `fetchWithAdminAuth(url, options)` | 带认证的 fetch（无超时，401 跳转登录） |

#### core/api/history.ts
历史记录 API 客户端：

| 函数 | 说明 |
|------|------|
| `getHistoryList(cursor, size)` | 获取历史列表（游标分页） |
| `getHistoryDetail(shortId)` | 获取单条记录详情 |
| `deleteHistory(shortId)` | 删除记录 |
| `createShareUrl(shortId)` | 生成分享链接 |
| `getSharedRecord(shortId, token)` | 通过分享 token 获取记录 |
| `generateStructuredQuestions(prompt)` | 生成结构化题目 |
| `getHistoryQuestions(shortId)` | 获取试卷题目详情 |
| `getHistoryAnswers(shortId)` | 获取整卷答案 |

### 3.3 功能模块 (features/)

#### features/auth/
认证相关功能：
- `LoginPage.tsx`: 登录/注册页面（含注册后年级选择）
- `LoginModal.tsx`: 登录弹窗组件

#### features/question-generator/
题目生成相关功能：
- `MainContent.tsx`: 主工作台界面
  - 快捷模板选择
  - 提示词输入
  - 题目预览
  - 打印/导出功能
- `StructuredPreview.tsx`: 结构化题目预览页
- `ProgressModal.tsx`: 生成进度提示弹窗

#### features/history/
历史记录相关功能：
- `HistoryList.tsx`: 历史记录下拉列表
- `HistoryDetail.tsx`: 历史记录详情页
- `SharePage.tsx`: 公开分享页（无需登录）

#### features/landing/
落地页功能：
- `LandingPage.tsx`: 首页落地页

### 3.4 组件模块 (components/)

#### components/questions/
题型组件 - 每种题型独立组件：

| 组件 | 题型 | 适用范围 |
|------|------|---------|
| `SingleChoice.tsx` | 单选题 | 全学科 |
| `MultipleChoice.tsx` | 多选题 | 全学科 |
| `TrueFalse.tsx` | 判断题 | 全学科 |
| `FillBlank.tsx` | 填空题 | 全学科 |
| `Calculation.tsx` | 计算题 | 数学 |
| `WordProblem.tsx` | 应用题 | 数学 |
| `ReadComp.tsx` | 阅读理解 | 语文/英语 |
| `Cloze.tsx` | 完形填空 | 英语 |
| `Essay.tsx` | 作文题 | 语文/英语 |

#### components/shared/
通用 UI 组件库：

| 组件 | 说明 | Props |
|------|------|-------|
| `Button` | 按钮组件 | variant, size, loading, leftIcon, rightIcon |
| `LoadingSpinner` | 加载动画 | size, text |
| `Modal` | 模态框 | isOpen, onClose, title, size |

**变体类型**:
- `Button`: primary, secondary, success, danger, ghost
- `LoadingSpinner`: small, medium, large
- `Modal`: small, medium, large

#### components/GradeSelectorModal.tsx
年级选择器弹窗组件 - 用户注册后或老用户未填写年级时弹出：

```typescript
// 年级选项
const PRIMARY_GRADES = [
  { value: 'grade1', label: '一年级' },
  // ... grade2~grade6
]
const JUNIOR_GRADES = [
  { value: 'grade7', label: '初一' },
  // ... grade8, grade9
]

// Props
interface GradeSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  onSelect: (grade: string) => Promise<void>
}
```

#### components/QuestionRenderer.tsx
题目渲染器 - 根据题型动态选择对应组件：

```typescript
// 伪代码示例
const QuestionRenderer = ({ question, index }) => {
  switch (question.type) {
    case 'SINGLE_CHOICE':
      return <SingleChoice {...props} />
    case 'FILL_BLANK':
      return <FillBlank {...props} />
    // ... 其他题型
  }
}
```

### 3.5 管理后台 (admin/)

#### admin/pages/
管理页面：
- `LoginPage.tsx`: 管理员登录
- `UsersPage.tsx`: 用户管理列表
- `UserDetailPage.tsx`: 用户详情
- `AiRecordsPage.tsx`: AI 生成记录
- `AiRecordDetailPage.tsx`: AI 记录详情
- `OperationLogsPage.tsx`: 操作日志

#### admin/services/api.ts
管理后台 API 客户端

### 3.6 工具模块 (utils/)

#### utils/promptValidator.ts
提示词输入校验：
- 空值检查
- 长度限制
- 敏感词过滤

#### utils/markdownProcessor.ts
Markdown 处理：
- Markdown 转 HTML
- 内联 Markdown 渲染（用于填空题等）

#### utils/printUtils.ts
打印和导出功能：
- 生成打印用 HTML（题目 + 答案分页）
- 调用浏览器打印接口
- PDF 导出支持

---

## 3.7 Hooks 模块 (hooks/)

### hooks/useMathJax.ts
MathJax 渲染自定义 Hooks：

| Hook | 说明 | 使用场景 |
|------|------|---------|
| `useMathJax(containerRef, options)` | 完整的 MathJax 渲染控制 | 需要手动控制渲染的场景 |
| `useMathJaxSimple(containerRef, deps)` | 简化的自动渲染 | 简单的题目列表渲染 |

**配置选项**:
- `autoRender`: 是否自动渲染（默认 true）
- `renderDelay`: 延迟渲染时间（默认 100ms）
- `watchDependencies`: 依赖变化时重新渲染（默认 true）

**使用示例**:
```typescript
const containerRef = useRef<HTMLDivElement>(null)
useMathJaxSimple(containerRef, [questions])
```

---

## 4. 类型定义 (types/)

### 4.1 types/index.ts
通用类型定义：

```typescript
// 用户相关
interface User  // 用户信息（含 grade 字段）

// 历史记录相关
interface GenerateResponse
interface QuestionRecord
interface QuestionRecordListItem
interface QuestionRecordListResponse
interface ShareUrlResponse
```

### 4.2 types/question.ts
题目相关类型：

```typescript
// 基础类型
type Subject = 'math' | 'chinese' | 'english'
type Grade = 'grade1' | ... | 'grade9'
type QuestionType = 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE' | ...

// 接口定义
interface MetaData        // 完整元数据（学科、年级、标题）
interface RecordMeta      // 精简元数据（历史记录用）
interface BaseQuestion
interface QuestionWithOptions
interface QuestionWithPassage
interface Question
interface StructuredQuestion

// 组件 Props
interface QuestionRendererProps
interface SingleChoiceProps
interface FillBlankProps
// ... 其他题型 Props
```

### 4.3 types/mathjax.ts
MathJax 全局类型扩展：

```typescript
interface MathJaxConfig {
  tex?: {...}
  options?: {...}
  svg?: {...}
  typeset?: (elements: HTMLElement[]) => void
  typesetPromise?: (elements: HTMLElement[]) => Promise<void>
}

declare global {
  interface Window {
    MathJax?: MathJaxConfig
  }
}
```

### 4.4 types/structured.ts
结构化数据类型（可选，用于复杂场景）

---

## 5. 配置文件

### 5.1 package.json
项目配置和脚本：

```json
{
  "scripts": {
    "dev": "vite",           // 开发模式
    "build": "tsc && vite build",  // 生产构建
    "preview": "vite preview",     // 预览构建产物
    "deploy": "npm run build && wrangler pages deploy dist"  // 部署
  }
}
```

### 5.2 tsconfig.json
TypeScript 配置：
- 严格模式启用
- 目标 ES2020
- Module Resolution: bundler

### 5.3 vite.config.ts
Vite 配置：
- React 插件
- 路径别名配置
- 代理配置（开发环境）

---

## 6. 代码规范

### 6.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `MainContent.tsx` |
| 组件名 | PascalCase | `const QuestionRenderer = () => {}` |
| 函数/变量 | camelCase | `const fetchUser = () => {}` |
| 类型/接口 | PascalCase | `interface QuestionRecord` |
| 常量 | UPPER_SNAKE_CASE | `const REQUEST_TIMEOUT = 120000` |
| 文件路径 | kebab-case | `features/question-generator/` |

### 6.2 文件组织

每个 `.tsx` 文件遵循以下顺序：
1. 导入语句（React → 第三方库 → 本地模块）
2. 类型定义
3. 常量定义
4. 组件主逻辑
5. 导出语句

### 6.3 组件结构

```typescript
// 1. 导入
import { useState } from 'react'
import type { Question } from '@/types'

// 2. Props 类型
interface Props {
  email: string
  onLogout: () => void
}

// 3. 组件
export default function Component({ email, onLogout }: Props) {
  // 3.1 State
  const [data, setData] = useState([])

  // 3.2 Effects
  useEffect(() => { ... }, [])

  // 3.3 事件处理
  const handleClick = () => { ... }

  // 3.4 渲染
  return <div>...</div>
}
```

---

## 7. 依赖说明

### 7.1 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| react | ^19.x | UI 框架 |
| react-dom | ^19.x | React DOM 渲染 |
| react-router-dom | ^7.x | 路由管理 |

### 7.2 工具库

| 包名 | 版本 | 用途 |
|------|------|------|
| marked | ^17.x | Markdown 解析 |
| mathjax | ^4.x | 数学公式渲染 |
| markdown-it | ^14.x | Markdown 解析（备用） |

### 7.3 开发依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| typescript | ~5.9.x | TypeScript 编译器 |
| vite | ^7.x | 构建工具 |
| @vitejs/plugin-react | ^5.x | Vite React 插件 |
| @cloudflare/workers-types | ^4.x | Cloudflare Workers 类型 |
| wrangler | ^3.x | Cloudflare 部署工具 |

---

## 8. 构建与部署

### 8.1 开发环境

```bash
# 启动开发服务器（默认端口 5173）
npm run dev
```

开发服务器特性：
- 热模块替换 (HMR)
- TypeScript 类型检查
- ESLint 检查（如配置）

### 8.2 生产构建

```bash
# 构建到 dist/ 目录
npm run build
npm run build:cf
```

构建产物：
- 代码压缩混淆
- CSS 提取和压缩
- 资源指纹（[hash]）
- Tree Shaking

### 8.3 部署

```bash
# 构建并部署到 Cloudflare Pages
npm run deploy
npx wrangler pages deploy dist --project-name=zyb-frontend --commit-dirty=true
```

部署要求：
- Cloudflare 账号
- `wrangler` CLI 认证

---

## 附录

### A. 相关文档
- [前端系统架构](./frontend-system-architecture.md)
- [前后端交互逻辑](./frontend-backend-interaction-logic.md)

### B. 常用命令速查

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 生产构建 |
| `npm run build:cf` | Cloudflare 特定构建 |
| `npm run preview` | 预览构建产物 |
| `npm run deploy` | 部署到 Cloudflare |
