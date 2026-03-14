# 前后端交互逻辑文档

## 1. 概述

### 1.1 交互架构

```
┌─────────────────┐                           ┌─────────────────┐
│     前端        │                           │     后端        │
│   (React SPA)   │                           │  (FastAPI)      │
├─────────────────┤                           ├─────────────────┤
│ - Axios/Fetch   │────── HTTPS ─────────────▶│ - RESTful API   │
│ - Token 管理    │◀────── JSON ──────────────│ - JWT 认证      │
│ - 状态管理      │                           │ - 业务逻辑      │
└─────────────────┘                           └─────────────────┘
```

### 1.2 通信协议

| 项目 | 说明 |
|------|------|
| 协议 | HTTPS (生产) / HTTP (开发) |
| 数据格式 | JSON |
| 认证方式 | Bearer Token (JWT) |
| CORS | 后端配置允许的来源 |

### 1.3 基础 URL

| 环境 | 前端配置 | 后端地址 |
|------|---------|---------|
| 开发 | `/api` (代理) | http://localhost:8000 |
| 生产 | `/api` (相对路径) | 同域名后端服务 |

---

## 2. 认证交互流程

### 2.1 用户注册

```
前端                                     后端
 │                                         │
 │  1. 输入邮箱，点击获取验证码             │
 ├────────────────────────────────────────▶│
 │     POST /api/auth/send-otp             │
 │     { "email": "user@example.com" }     │
 │                                         │
 │  2. 返回发送成功                        │
 │◀────────────────────────────────────────┤
 │     { "message": "验证码已发送" }       │
 │                                         │
 │  3. 用户输入验证码和密码                 │
 ├────────────────────────────────────────▶│
 │     POST /api/auth/register             │
 │     {                                    │
 │       "email": "user@example.com",      │
 │       "password": "******",             │
 │       "code": "123456"                  │
 │     }                                   │
 │                                         │
 │  4. 返回 JWT Token                      │
 │◀────────────────────────────────────────┤
 │     { "access_token": "eyJ..." }        │
 │                                         │
 │  5. 存储 Token 到 localStorage          │
 │                                         │
```

### 2.2 用户登录

```
前端                                     后端
 │                                         │
 │  1. 输入邮箱和密码                       │
 ├────────────────────────────────────────▶│
 │     POST /api/auth/login                │
 │     {                                    │
 │       "email": "user@example.com",      │
 │       "password": "******"              │
 │     }                                   │
 │                                         │
 │  2. 验证密码，返回 JWT Token             │
 │◀────────────────────────────────────────┤
 │     { "access_token": "eyJ..." }        │
 │                                         │
 │  3. 存储 Token 到 localStorage          │
 │                                         │
```

### 2.3 带认证的请求

```typescript
// frontend/src/core/auth/userAuth.ts
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken()  // 从 localStorage 获取
  const headers = new Headers(options.headers)
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(url, { ...options, headers })

  // 处理 401 未授权
  if (response.status === 401) {
    clearToken()
    window.location.href = '/'
  }

  return response
}
```

### 2.4 Token 过期处理

```
前端                                     后端
 │                                         │
 │  1. 携带 Token 发起请求                  │
 ├────────────────────────────────────────▶│
 │     GET /api/history                    │
 │     Authorization: Bearer <expired>     │
 │                                         │
 │  2. Token 过期，返回 401                │
 │◀────────────────────────────────────────┤
 │     401 Unauthorized                    │
 │     { "detail": "登录已过期" }          │
 │                                         │
 │  3. 清除 Token，跳转登录页               │
 │                                         │
```

---

## 3. 题目生成交互

### 3.1 结构化题目生成

```
前端                                     后端
 │                                         │
 │  1. 用户输入提示词，点击生成             │
 ├────────────────────────────────────────▶│
 │     POST /api/questions/structured      │
 │     {                                    │
 │       "prompt": "三年级数学乘法"         │
 │     }                                   │
 │                                         │
 │  2. 显示进度条                          │
 │     - preparing                         │
 │     - connecting                        │
 │     - generating                        │
 │     - processing                        │
 │     - complete                          │
 │                                         │
 │  3. AI 生成题目，解析 JSON               │
 │     数据清洗，计算 rows_to_answer       │
 │     保存记录到数据库                     │
 │                                         │
 │  4. 返回结构化数据                       │
 │◀────────────────────────────────────────┤
 │     {                                    │
 │       "meta": {                          │
 │         "subject": "math",               │
 │         "grade": "grade3",               │
 │         "title": "三年级数学乘法"        │
 │       },                                 │
 │       "questions": [                     │
 │         {                                │
 │           "type": "CALCULATION",         │
 │           "stem": "计算 23 × 45",        │
 │           "knowledge_points": [...],     │
 │           "rows_to_answer": 3            │
 │         }                                │
 │       ],                                 │
 │       "record_id": 123,                  │
 │       "short_id": "abc123"               │
 │     }                                    │
 │                                         │
 │  5. 渲染题目到预览区                     │
 │                                         │
```

### 3.2 题目渲染

```typescript
// frontend/src/components/QuestionRenderer.tsx
const QuestionRenderer = ({ question, index, mode }) => {
  switch (question.type) {
    case 'SINGLE_CHOICE':
      return <SingleChoice question={question} index={index} />
    case 'FILL_BLANK':
      return <FillBlank question={question} index={index} />
    case 'CALCULATION':
      return <Calculation question={question} index={index} />
    // ... 其他题型
    default:
      return <div>未知题型</div>
  }
}
```

---

## 4. 历史记录交互

### 4.1 获取历史记录列表

```
前端                                     后端
 │                                         │
 │  1. 用户打开历史记录下拉框               │
 ├────────────────────────────────────────▶│
 │     GET /api/history?cursor=0&size=20   │
 │                                         │
 │  2. 查询用户记录（游标分页）             │
 │     按 created_at DESC 排序              │
 │                                         │
 │  3. 返回历史记录列表                     │
 │◀────────────────────────────────────────┤
 │     {                                    │
 │       "data": [                          │
 │         {                                │
 │           "id": 123,                     │
 │           "short_id": "abc123",          │
 │           "title": "三年级数学乘法",     │
 │           "created_at": "2024-01-01..."  │
 │         }                                │
 │       ],                                 │
 │       "next_cursor": 123,                │
 │       "has_more": true                   │
 │     }                                    │
 │                                         │
 │  4. 渲染历史记录列表                     │
 │                                         │
```

### 4.2 查看历史记录详情

```
前端                                     后端
 │                                         │
 │  1. 用户点击某条历史记录                 │
 ├────────────────────────────────────────▶│
 │     GET /api/history/{short_id}         │
 │                                         │
 │  2. 查询记录详情                         │
 │                                         │
 │  3. 返回记录详情（含 AI 原始响应）       │
 │◀────────────────────────────────────────┤
 │     {                                    │
 │       "id": 123,                         │
 │       "title": "...",                    │
 │       "ai_response": "Markdown 内容",    │
 │       "created_at": "..."                │
 │     }                                    │
 │                                         │
```

### 4.3 获取试卷题目（含答案）

```
前端                                     后端
 │                                         │
 │  1. 用户查看试卷详情                     │
 ├────────────────────────────────────────▶│
 │     GET /api/history/{short_id}/questions│
 │                                         │
 │  2. 查询试卷下所有题目                   │
 │     含 rows_to_answer, answer_text      │
 │                                         │
 │  3. 返回题目列表                         │
 │◀────────────────────────────────────────┤
 │     {                                    │
 │       "meta": {                          │
 │         "record_id": 123,                │
 │         "short_id": "abc123",            │
 │         "title": "..."                   │
 │       },                                 │
 │       "questions": [                     │
 │         {                                │
 │           "id": 1,                       │
 │           "type": "CALCULATION",         │
 │           "stem": "...",                 │
 │           "rows_to_answer": 3,           │
 │           "answer_text": "..."           │
 │         }                                │
 │       ]                                  │
 │     }                                    │
 │                                         │
```

---

## 5. 分享功能交互

### 5.1 生成分享链接

```
前端                                     后端
 │                                         │
 │  1. 用户点击分享按钮                     │
 ├────────────────────────────────────────▶│
 │     POST /api/history/{short_id}/share  │
 │                                         │
 │  2. 生成或获取 share_token              │
 │     保存到数据库                         │
 │                                         │
 │  3. 返回分享链接                         │
 │◀────────────────────────────────────────┤
 │     {                                    │
 │       "share_url": "/share/h/abc123?    │
 │                      token=xyz789"       │
 │     }                                    │
 │                                         │
 │  4. 前端拼接完整 URL，用户复制           │
 │     https://your-domain.com/share/...   │
 │                                         │
```

### 5.2 访问分享链接

```
前端 (分享页)                              后端
 │                                         │
 │  1. 用户打开分享链接                     │
 │     /share/h/{short_id}?token=xyz       │
 │                                         │
 │  2. 解析 URL 参数                        │
 │                                         │
 ├────────────────────────────────────────▶│
 │     GET /api/share/history/{short_id}/  │
 │                        questions?token=  │
 │                                         │
 │  3. 验证 token 有效性                    │
 │     查询题目数据                         │
 │                                         │
 │  4. 返回题目数据（无需登录）             │
 │◀────────────────────────────────────────┤
 │     {                                    │
 │       "meta": {...},                     │
 │       "questions": [...]                 │
 │     }                                    │
 │                                         │
 │  5. 渲染题目到页面（公开访问）           │
 │                                         │
```

---

## 6. 数据结构定义

### 6.1 请求/响应数据结构

#### 注册请求
```typescript
interface RegisterRequest {
  email: string
  password: string
  code: string  // 6 位验证码
}
```

#### 登录请求
```typescript
interface LoginRequest {
  email: string
  password: string
}
```

#### Token 响应
```typescript
interface TokenResponse {
  access_token: string
  token_type?: string  // "bearer"
}
```

#### 结构化题目生成响应
```typescript
interface StructuredGenerateResponse {
  meta: MetaData
  questions: StructuredQuestion[]
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
  stem: string
  knowledge_points: string[]
  options?: string[]
  passage?: string
  sub_questions?: Question[]
  rows_to_answer: number
  answer_blanks?: number
  answer_text?: string
}
```

#### 历史记录列表响应
```typescript
interface QuestionRecordListResponse {
  data: QuestionRecordListItem[]
  next_cursor: number | null
  has_more: boolean
}

interface QuestionRecordListItem {
  id: number
  short_id: string
  title: string
  created_at: string
}
```

---

## 7. 错误处理

### 7.1 HTTP 状态码

| 状态码 | 说明 | 前端处理 |
|--------|------|---------|
| 200 | 成功 | 正常处理响应数据 |
| 400 | 请求错误 | 显示错误消息（如提示词为空） |
| 401 | 未授权 | 清除 Token，跳转登录 |
| 403 | 禁止访问 | 显示权限不足 |
| 404 | 资源不存在 | 显示资源不存在 |
| 429 | 请求过于频繁 | 显示请稍后重试 |
| 500 | 服务器错误 | 显示系统错误 |
| 502 | AI 服务错误 | 显示 AI 服务异常 |

### 7.2 前端错误处理示例

```typescript
// frontend/src/features/question-generator/MainContent.tsx
const generate = async () => {
  try {
    const data = await generateStructuredQuestions(p)
    setQuestions(data.questions)
    setMeta(data.meta)
  } catch (e) {
    let errorMessage = '生成失败，请稍后重试'
    if (e instanceof Error) {
      if (e.message.includes('超时')) {
        errorMessage = '题目生成时间过长，请减少题目数量或简化要求后重试'
      } else if (e.message.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络后重试'
      } else {
        errorMessage = e.message
      }
    }
    setError(errorMessage)
  }
}
```

### 7.3 后端错误响应格式

```json
{
  "detail": "错误消息内容"
}
```

---

## 8. 超时控制

### 8.1 前端超时

```typescript
// frontend/src/core/auth/userAuth.ts
const REQUEST_TIMEOUT = 120 * 1000  // 120 秒

export async function fetchWithAuth(...) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => {
    controller.abort()
  }, REQUEST_TIMEOUT)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    return response
  } catch (error) {
    clearTimeout(timeoutId)
    if (error.name === 'AbortError') {
      throw new Error('请求超时，题目生成时间过长，请稍后重试')
    }
    throw error
  }
}
```

### 8.2 后端 AI 调用超时

```python
# backend/services/qwen_client.py
async def generate_questions_async(user_prompt, user_id):
    # Batch 等待时间：最多 3 秒
    # API 调用时间：单个请求最多 30 秒
    content = await loop.run_in_executor(
        None,
        lambda: future.result(timeout=30)
    )
```

---

## 9. 打印导出交互

### 9.1 打印流程

```
前端
 │
 │  1. 用户点击打印按钮
 │
 │  2. 调用 handlePrint
 │     - 生成题目 HTML（不含答案）
 │     - 生成答案 HTML（单独页）
 │     - 使用 MathJax 渲染公式
 │
 │  3. 调用 window.print()
 │     - 用户选择打印机
 │     - 或"另存为 PDF"
 │
```

---

## 10. API 端点汇总

### 10.1 用户认证

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/auth/send-otp | 否 | 发送验证码 |
| POST | /api/auth/register | 否 | 注册 |
| POST | /api/auth/login | 否 | 登录 |
| POST | /api/auth/reset-password | 否 | 重置密码 |
| GET | /api/auth/me | 是 | 获取当前用户 |
| POST | /api/auth/logout | 是 | 登出 |

### 10.2 题目生成

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/questions/structured | 是 | 生成结构化题目 |

### 10.3 历史记录

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| GET | /api/history | 是 | 历史记录列表 |
| GET | /api/history/{short_id} | 是 | 记录详情 |
| GET | /api/history/{short_id}/questions | 是 | 试卷题目 |
| GET | /api/history/{short_id}/answers | 是 | 整卷答案 |
| DELETE | /api/history/{short_id} | 是 | 删除记录 |
| POST | /api/history/{short_id}/share | 是 | 生成分享链接 |

### 10.4 分享接口（公开）

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| GET | /api/share/history/{short_id} | 否 | 分享记录详情 |
| GET | /api/share/history/{short_id}/questions | 否 | 分享题目 |
| GET | /api/share/history/{short_id}/answers | 否 | 分享答案 |

### 10.5 管理后台

| 方法 | 端点 | 认证 | 说明 |
|------|------|------|------|
| POST | /api/admin/login | 否 | 管理员登录 |
| GET | /api/admin/users | 是 | 用户列表 |
| GET | /api/admin/users/{user_id} | 是 | 用户详情 |
| POST | /api/admin/users/{user_id}/disable | 是 | 禁用用户 |
| GET | /api/admin/ai-records | 是 | AI 记录列表 |

---

## 附录

### A. 相关文档
- [前端系统架构](./frontend-system-architecture.md)
- [后端系统架构](./backend-system-architecture.md)
- [前端代码结构](./frontend-code-structure.md)
- [后端代码结构](./backend-code-structure.md)

### B. 调试工具

| 工具 | 用途 |
|------|------|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Postman | API 接口测试 |
| Chrome DevTools | 网络请求调试 |
