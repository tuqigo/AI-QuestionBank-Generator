# API 接口文档

> 题小宝 AI 题库生成器 - 完整 API 接口说明

**Base URL**: `http://localhost:8000`

**Swagger 文档**: `http://localhost:8000/docs`

---

## 认证说明

大部分接口需要 JWT Token 认证。

### 获取 Token

```bash
# 登录接口
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}

# 响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 使用 Token

在请求头中添加：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 认证接口 (Auth)

### POST /api/auth/send-otp

发送邮箱验证码

**请求：**
```json
{
  "email": "user@example.com",
  "purpose": "register"  // 或 "reset_password"
}
```

**响应：**
```json
{
  "message": "验证码已发送",
  "email": "user@example.com"
}
```

**错误码：**
- `400`: 邮箱格式无效 / 该邮箱已被注册 / 该邮箱未注册
- `429`: 请求过于频繁

---

### POST /api/auth/register

用户注册

**请求：**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "code": "123456"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**错误码：**
- `400`: 邮箱格式无效 / 密码无效 / 验证码错误
- `400`: 该邮箱已被注册

---

### POST /api/auth/login

用户登录

**请求：**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**错误码：**
- `400`: 邮箱格式无效
- `401`: 邮箱或密码错误 / 请先设置密码

---

### POST /api/auth/reset-password

重置密码

**请求：**
```json
{
  "email": "user@example.com",
  "code": "123456",
  "new_password": "newpassword123"
}
```

**响应：**
```json
{
  "message": "密码重置成功"
}
```

**错误码：**
- `400`: 验证码错误 / 密码无效 / 用户不存在

---

### GET /api/auth/me

获取当前用户信息

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "email": "user@example.com"
}
```

**错误码：**
- `401`: 未登录 / 登录已过期 / 用户不存在

---

### POST /api/auth/logout

用户登出

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "message": "登出成功"
}
```

---

## 题目生成接口 (Questions)

### POST /api/questions/generate

根据提示词生成题目

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求：**
```json
{
  "prompt": "生成三年级数学加减法练习题 10 道"
}
```

**响应：**
```json
{
  "title": "三年级数学加减混合练习",
  "markdown": "# 三年级数学加减混合练习\n\n1. 计算：256 + 144 = ?\n\n2. 计算：800 - 356 = ?\n\n...",
  "record_id": 123,
  "short_id": "abc123"
}
```

**错误码：**
- `400`: 提示词不能为空 / 提示词校验失败
- `404`: 用户不存在
- `500`: 题目生成失败
- `502`: API 错误

---

### POST /api/questions/generate-structured

结构化方式生成题目 (JSON Schema)

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求：**
```json
{
  "subject": "math",
  "grade": "grade3",
  "questionTypes": ["SINGLE_CHOICE", "CALCULATION"],
  "count": 10
}
```

**响应：**
```json
{
  "meta": {
    "subject": "math",
    "grade": "grade3",
    "title": "三年级数学同步练习"
  },
  "questions": [
    {
      "type": "SINGLE_CHOICE",
      "stem": "计算 256 + 144 的结果是？",
      "options": ["400", "500", "600", "450"],
      "knowledge_points": ["万以内加法计算"]
    }
  ]
}
```

**错误码：**
- `400`: 参数校验失败
- `500`: 生成失败

---

### POST /api/questions/extend-from-image

上传图片生成扩展题

**请求头：**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `image` | File | 是 | 题目图片 |
| `count` | Integer | 否 | 扩展题数量，默认 5 |

**响应：**
```json
{
  "title": "同类扩展题",
  "markdown": "# 扩展题目\n\n1. 计算：...\n\n...",
  "record_id": 124,
  "short_id": "def456"
}
```

**错误码：**
- `400`: 图片格式不支持
- `500`: 识别失败

---

## 历史记录接口 (History)

### GET /api/history

获取历史记录列表

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | Integer | 1 | 页码 |
| `page_size` | Integer | 10 | 每页数量 |

**响应：**
```json
{
  "total": 50,
  "items": [
    {
      "id": 123,
      "short_id": "abc123",
      "title": "三年级数学练习",
      "created_at": "2026-03-14T10:00:00",
      "prompt_type": "text"
    }
  ]
}
```

---

### GET /api/history/:id

获取单条记录详情

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "id": 123,
  "short_id": "abc123",
  "title": "三年级数学练习",
  "ai_response": "# 题目内容\n\n...",
  "created_at": "2026-03-14T10:00:00",
  "is_shared": false
}
```

**错误码：**
- `404`: 记录不存在

---

### POST /api/history/:id/share

生成分享链接

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "share_id": "xyz789",
  "share_url": "http://localhost:5173/share/h/xyz789"
}
```

---

### POST /api/history/:id/copy

复制记录到目标用户 (运营功能)

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "message": "复制成功",
  "new_id": 456
}
```

---

## 管理后台接口 (Admin)

### GET /api/admin/stats

获取统计数据

**请求头：**
```
Authorization: Bearer <admin-token>
```

**响应：**
```json
{
  "total_users": 100,
  "total_records": 500,
  "today_records": 20,
  "total_ai_calls": 600
}
```

---

### GET /api/admin/users

获取用户列表

**请求头：**
```
Authorization: Bearer <admin-token>
```

**查询参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | Integer | 1 | 页码 |
| `page_size` | Integer | 20 | 每页数量 |

**响应：**
```json
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "email": "user1@example.com",
      "created_at": "2026-01-01T00:00:00",
      "record_count": 10
    }
  ]
}
```

---

### GET /api/admin/records

获取题目记录列表

**请求头：**
```
Authorization: Bearer <admin-token>
```

**响应：**
```json
{
  "total": 500,
  "items": [
    {
      "id": 123,
      "user_id": 1,
      "user_email": "user@example.com",
      "title": "三年级数学练习",
      "created_at": "2026-03-14T10:00:00"
    }
  ]
}
```

---

### GET /api/admin/logs

获取操作日志

**请求头：**
```
Authorization: Bearer <admin-token>
```

**响应：**
```json
{
  "total": 1000,
  "items": [
    {
      "id": 1,
      "operation": "生成题目",
      "user_email": "user@example.com",
      "created_at": "2026-03-14T10:00:00"
    }
  ]
}
```

---

## 错误码汇总

| 状态码 | 说明 |
|--------|------|
| `200` | 成功 |
| `400` | 请求参数错误 |
| `401` | 未认证/Token 无效 |
| `403` | 无权限 |
| `404` | 资源不存在 |
| `429` | 请求过于频繁 |
| `500` | 服务器内部错误 |
| `502` | 第三方 API 错误 |

---

## 速率限制

| 接口 | 限制 |
|------|------|
| 发送验证码 | 5 次/分钟，最多 5 次/60 分钟 |
| 题目生成 | 根据 API Key 配额 |
| 其他接口 | 无限制 |

---

## 请求示例 (cURL)

```bash
# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 获取用户信息
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# 生成题目
curl -X POST http://localhost:8000/api/questions/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt":"生成三年级数学练习题 10 道"}'

# 获取历史记录
curl -X GET "http://localhost:8000/api/history?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

*最后更新：2026-03-14*
