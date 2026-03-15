# 前端系统架构文档

## 1. 系统概述

### 1.1 项目简介

**题小宝** - 小学生 AI 题库生成器的前端系统，是一个基于 React 19 + TypeScript 的单页应用（SPA），用于生成和管理 K12 阶段的数学、语文、英语练习题。

### 1.2 技术选型

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 核心框架 | React | 19.x | 函数组件 + Hooks |
| 语言 | TypeScript | 7.x | 类型安全 |
| 构建工具 | Vite | 7.x | 快速开发和构建 |
| 路由 | React Router | 7.x | 客户端路由管理 |
| Markdown 渲染 | marked | 17.x | Markdown 解析 |
| 数学公式 | MathJax | 3.x | LaTeX 公式渲染（typesetPromise API） |
| 部署平台 | Cloudflare Pages | - | 静态资源托管 |

### 1.3 系统目标

- 提供直观友好的题目生成界面
- 支持多种题型的结构化展示
- 实现历史记录管理和分享功能
- 支持 PDF 导出和打印功能

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层 (UI Layer)                      │
├─────────────────────────────────────────────────────────────────┤
│  LandingPage  │  LoginPage  │  MainContent  │  HistoryDetail   │
│  SharePage    │  StructuredPreview  │  AdminApp                 │
├─────────────────────────────────────────────────────────────────┤
│                        组件层 (Components)                        │
├─────────────────────────────────────────────────────────────────┤
│  QuestionRenderer  │  StructuredPreviewShared  │  Modal  等     │
├─────────────────────────────────────────────────────────────────┤
│                     题型组件层 (Question Types)                    │
├─────────────────────────────────────────────────────────────────┤
│  SingleChoice │ MultipleChoice │ FillBlank │ Calculation │ ...  │
├─────────────────────────────────────────────────────────────────┤
│                        服务层 (Services)                          │
├─────────────────────────────────────────────────────────────────┤
│  userAuth.ts  │  adminAuth.ts  │  history.ts  │  API 客户端     │
├─────────────────────────────────────────────────────────────────┤
│                        工具层 (Utils)                             │
├─────────────────────────────────────────────────────────────────┤
│  printUtils.ts  │  markdownProcessor.ts  │  promptValidator.ts  │
├─────────────────────────────────────────────────────────────────┤
│                        状态/数据层                                │
├─────────────────────────────────────────────────────────────────┤
│  React State (Hooks)  │  LocalStorage (Token)  │  Window 对象   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 分层架构说明

#### 2.2.1 用户界面层（Pages）
- **LandingPage**: 首页/落地页，公开访问
- **LoginPage**: 登录/注册页面（含注册后年级选择）
- **MainContent**: 主工作台，题目生成和预览
- **HistoryDetail**: 历史记录详情查看
- **SharePage**: 公开分享页面
- **StructuredPreview**: 结构化题目预览页
- **AdminApp**: 管理后台入口

#### 2.2.2 组件层（Components）
- **QuestionRenderer**: 题目渲染器，根据题型动态选择组件
- **StructuredPreviewShared**: 结构化题目预览共享组件
- **ProgressModal**: 进度提示弹窗
- **LoginModal**: 登录弹窗
- **GradeSelectorModal**: 年级选择弹窗（新用户注册后/老用户未填写时显示）
- **Shared UI 组件库** (`components/shared/`):
  - `Button`: 通用按钮组件（支持 variant/size/loading）
  - `LoadingSpinner`: 加载动画组件
  - `Modal`: 模态框组件（支持 ESC 关闭）

#### 2.2.3 题型组件层（Question Type Components）
每种题型对应独立组件，遵循统一 props 接口：
- **SingleChoice.tsx**: 单选题
- **MultipleChoice.tsx**: 多选题
- **TrueFalse.tsx**: 判断题
- **FillBlank.tsx**: 填空题
- **Calculation.tsx**: 计算题
- **WordProblem.tsx**: 应用题
- **ReadComp.tsx**: 阅读理解
- **Cloze.tsx**: 完形填空
- **Essay.tsx**: 作文题

#### 2.2.4 服务层（Services）
- **auth/**: 认证服务
  - `authFactory.ts`: 认证工厂模式（统一错误处理、401 响应处理）
  - `userAuth.ts`: C 端用户认证（token 管理、120s 超时 fetch）
  - `adminAuth.ts`: 管理后台认证（无超时、401 跳转）
- **api/**: API 客户端
  - `history.ts`: 历史记录相关 API 调用

#### 2.2.5 工具层（Utils）
- `printUtils.ts`: 打印和 PDF 导出
- `markdownProcessor.ts`: Markdown 处理和 MathJax 渲染
- `promptValidator.ts`: 提示词输入校验

#### 2.2.6 自定义 Hooks
- `useMathJax`: MathJax 加载和渲染控制（支持配置选项）
- `useMathJaxSimple`: 简化版 MathJax Hook（依赖变化时自动渲染）

---

## 3. 核心模块设计

### 3.1 认证模块

#### 3.1.1 Token 管理

```
┌──────────────────────────────────────┐
│           用户登录                    │
│  输入邮箱/密码 → POST /api/auth/login│
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  服务端返回 JWT Token                 │
│  存储至 localStorage: qbank_token    │
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  后续请求自动携带 Authorization Header│
│  Bearer <token>                      │
└──────────────────────────────────────┘
```

#### 3.1.2 年级选择流程

```
┌──────────────────────────────────────┐
│  用户注册成功/登录                    │
│  调用 GET /api/auth/me 获取用户信息   │
└──────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ grade 是否为空？│
        └────────────────┘
            │          │
       是 (null)    否 (有值)
            │          │
            ▼          │
┌──────────────────┐   │
│ 弹出 GradeSelector│   │
│ 用户选择年级      │   │
│ PUT /api/users   │   │
│ /grade           │   │
└──────────────────┘   │
            │          │
            ▼          ▼
┌──────────────────────────────┐
│  更新本地用户状态，继续操作   │
└──────────────────────────────┘
```

#### 3.1.3 认证工厂模式

```typescript
// core/auth/authFactory.ts
// 使用工厂模式统一认证逻辑

// 1. 创建认证存储实例
const { getToken, setToken, clearToken } = createAuthStorage('qbank_token')

// 2. 创建带认证的 fetch 包装器
const { fetchWithAuth } = createFetchWithAuth(
  getToken,
  120000,  // 超时时间
  () => { /* 401 处理逻辑 */ }
)
```

**优势**:
- 统一错误处理（try-catch）
- 统一的 401 响应处理逻辑
- 支持可配置的超时时间
- 减少代码重复

#### 3.1.4 请求超时控制
- 所有 API 请求统一使用 `fetchWithAuth` 方法
- 超时时间：120 秒
- 使用 `AbortController` 实现可中断请求

### 3.2 题目生成模块

#### 3.2.1 生成流程

```
用户输入提示词
     │
     ▼
┌─────────────────┐
│  promptValidator│
│  输入校验        │
└─────────────────┘
     │
     ▼ (校验通过)
┌─────────────────┐
│  显示进度条      │
│  preparing →    │
│  connecting →   │
│  generating →   │
│  processing →   │
│  complete       │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ POST /api/      │
│ questions/      │
│ structured      │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  接收结构化 JSON │
│  更新 State      │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  QuestionRenderer│
│  动态渲染题目    │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  useMathJax     │
│  MathJax 渲染   │
└─────────────────┘
```

### 3.3 CSS 模块化架构

#### 3.3.1 模块化拆分

主界面 CSS 按功能模块拆分为独立文件：

| 文件 | 职责 | 行数 |
|------|------|------|
| `header.css` | 头部导航、历史记录下拉框、用户信息 | ~420 |
| `sidebar.css` | 侧边栏、提示词输入、快捷按钮、图片上传 | ~270 |
| `preview.css` | 预览区域、Markdown 内容、题目展示 | ~260 |
| `modals.css` | 弹窗组件、进度条 Modal、删除确认框 | ~260 |
| `MainContent.css` | 全局重置、布局、响应式（导入上述模块） | ~200 |

**优势**:
- 职责单一，易于维护
- 减少 CSS 冲突
- 便于删除或迁移功能模块

### 3.4 数学公式渲染模块

#### 3.4.1 MathJax Hook 封装

```typescript
// hooks/useMathJax.ts

// 完整版本 - 支持配置选项
const { isLoaded, isReady, hasRendered, render, reset } = useMathJax(
  containerRef,
  {
    autoRender: true,      // 是否自动渲染
    renderDelay: 100,      // 延迟渲染时间（ms）
    watchDependencies: true // 依赖变化时重新渲染
  }
)

// 简化版本 - 依赖变化时自动渲染
useMathJaxSimple(containerRef, [questions])
```

#### 3.4.2 MathJax 渲染策略

1. **加载检测**: 轮询检测 `window.MathJax.typesetPromise` 是否可用
2. **延迟渲染**: DOM 更新后延迟 150ms 再渲染，确保内容已就绪
3. **内容变化检测**: 通过 `questions.map(q => q.stem).join('|')` 检测内容变化
4. **避免重复渲染**: 使用 `mathJaxRenderedRef` 标记已渲染状态

### 3.5 历史记录模块

#### 3.5.1 数据流

```
┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│ HistoryList  │───▶│ history.ts API │───▶│ GET /api/    │
│  组件        │    │  客户端        │    │ history      │
└──────────────┘    └───────────────┘    └──────────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │ 游标分页       │
                    │ cursor/size   │
                    └───────────────┘
```

### 3.6 打印导出模块

#### 3.6.1 打印流程
1. 调用 `handlePrint` 方法
2. 生成带答案/不带答案的 HTML 内容
3. 调用浏览器打印接口
4. 用户可选择"另存为 PDF"

---

## 4. 数据流设计

### 4.1 状态管理策略

本项目采用 **React Hooks** 的轻量级状态管理方案：

| 状态类型 | 管理方式 | 存储位置 |
|---------|---------|---------|
| 用户认证状态 | useState + useEffect | localStorage + Window |
| 题目数据 | useState | 组件内存 |
| 历史记录列表 | useState | 组件内存 |
| 全局配置 | 静态导入 | 模块常量 |

### 4.2 共享组件数据流

`StructuredPreviewShared` 组件用于历史记录、分享页等场景：

```typescript
interface StructuredPreviewSharedProps {
  questions: StructuredQuestion[]  // 题目数据
  meta?: RecordMeta | null         // 元数据
  recordTitle?: string             // 历史记录标题
  mode?: 'render' | 'print'        // 渲染模式
}
```

**特点**:
- 独立的 MathJax 加载和渲染逻辑
- 支持题目内容变化时重新渲染
- 打印模式下隐藏答题区域

### 4.2 数据结构

#### 4.2.1 结构化题目数据

```typescript
interface StructuredGenerateResponse {
  meta: MetaData           // 元数据：学科、年级、标题
  questions: StructuredQuestion[]  // 题目列表
  record_id?: number
  short_id?: string
  created_at?: string
}

interface MetaData {
  subject: 'math' | 'chinese' | 'english'
  grade: 'grade1' | ... | 'grade9'
  title: string
}

interface StructuredQuestion {
  type: QuestionType
  stem: string                    // 题干
  knowledge_points: string[]      // 知识点
  options?: string[]              // 选项（选择题）
  passage?: string                // 阅读材料（阅读/完形）
  sub_questions?: Question[]      // 子题目（阅读/完形）
  rows_to_answer: number          // 预留作答行数
  answer_blanks?: number          // 填空数（填空题）
  answer_text?: string            // 参考答案
}
```

---

## 5. 路由设计

### 5.1 路由表

| 路径 | 组件 | 认证要求 | 说明 |
|------|------|---------|------|
| `/` | LandingPage | 否 | 首页/落地页 |
| `/workbench` | MainContent | 是 | 主工作台 |
| `/history/:id` | HistoryDetail | 是 | 历史详情 |
| `/share/h/:id` | SharePage | 否 | 公开分享页 |
| `/structured` | StructuredPreview | 是 | 结构化预览（测试） |
| `/admin/*` | AdminApp | 是 (Admin) | 管理后台 |

### 5.2 路由守卫

```typescript
// 受保护路由：重定向到首页
<Route
  path="/workbench"
  element={user ? <MainContent /> : <Navigate to="/" />}
/>
```

---

## 6. 部署架构

### 6.1 部署流程

```
本地开发 → npm run build → dist/ → Cloudflare Pages Deploy
```

### 6.2 环境变量

部署时需配置以下环境变量：
- `VITE_API_BASE`: 后端 API 地址（可选，默认使用相对路径）

### 6.3 构建产物

```
dist/
├── index.html          # 入口 HTML
├── assets/
│   ├── index-[hash].js # 主 bundle
│   └── *.css           # 样式文件
└── icon*.svg           # 静态资源
```

---

## 7. 非功能性设计

### 7.1 性能优化

| 优化点 | 策略 |
|--------|------|
| 代码分割 | React Router 懒加载 |
| 数学公式渲染 | useMathJax Hook 按需渲染 |
| 列表分页 | 游标分页，避免全量加载 |
| 构建优化 | Vite Tree Shaking |
| CSS 模块化 | 按功能拆分，减少冲突 |

### 7.2 安全设计

| 风险点 | 防护措施 |
|--------|---------|
| XSS 攻击 | marked 配置 sanitize |
| Token 泄露 | localStorage 存储，HTTPS 传输 |
| CSRF | JWT Token + SameSite Cookie |

### 7.3 可访问性 (A11y)

- 所有按钮包含 `aria-label` 属性
- 错误提示使用 `role="alert"`
- 表单控件关联 `label` 标签

---

## 8. 技术债务与改进方向

### 8.1 已完成优化

1. **CSS 模块化**: 将 1761 行的 MainContent.css 拆分为 4 个职责单一的模块文件
2. **MathJax Hook 抽象**: 创建可复用的 useMathJax 和 useMathJaxSimple hooks
3. **认证工厂模式**: 使用 authFactory.ts 统一认证逻辑，减少代码重复
4. **通用组件库**: 创建 Button、LoadingSpinner、Modal 三个基础组件

### 8.2 当前技术债务

1. 状态管理分散，未使用统一 Store
2. 部分组件 props 层级过深
3. 错误边界 (Error Boundary) 未完善

### 8.3 改进方向

1. 考虑引入 Zustand/Jotai 进行全局状态管理
2. 抽取更多可复用 Hooks
3. 完善单元测试覆盖率

---

## 附录

### A. 目录结构
参见 [frontend-code-structure.md](./frontend-code-structure.md)

### B. 题型组件 API
各题型组件统一遵循 `QuestionRendererProps` 接口

### C. 相关文档
- [前后端交互逻辑](./frontend-backend-interaction-logic.md)
- [后端系统架构](./backend-system-architecture.md)
