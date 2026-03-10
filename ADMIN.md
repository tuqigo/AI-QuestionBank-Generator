# 管理后台使用说明

## 快速开始

### 1. 配置管理员密码

编辑 `backend/.env` 文件，添加或修改以下配置：

```env
# 管理员密码（明文存储）
ADMIN_PASSWORD=your-secure-password

# 管理员 Token 有效期（分钟），默认 2 小时
ADMIN_JWT_EXPIRE_MINUTES=120
```

### 2. 启动后端

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端

```bash
cd frontend
npm run dev
```

### 4. 访问管理后台

浏览器访问：`http://localhost:5173/admin`

默认密码：`admin123`（首次使用请修改）

---

## 功能模块

### 用户管理

- **用户列表**：查看所有注册用户，支持分页浏览
- **用户详情**：查看用户详细信息，包括注册时间、题目生成次数、最近活动时间
- **禁用/启用用户**：可以禁用违规用户，禁用后用户无法登录
- **使用记录**：查看用户生成的所有题目记录

### 操作日志

- 记录所有管理员操作
- 包含操作类型、操作时间、IP 地址、操作对象
- 支持分页查看

---

## API 接口

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/admin/login` | POST | 否 | 管理员登录 |
| `/api/admin/me` | GET | 是 | 获取当前管理员状态 |
| `/api/admin/users` | GET | 是 | 用户列表（分页） |
| `/api/admin/users/{id}` | GET | 是 | 用户详情 |
| `/api/admin/users/{id}/disable` | POST | 是 | 禁用/启用用户 |
| `/api/admin/users/{id}/records` | GET | 是 | 用户题目记录 |
| `/api/admin/operation-logs` | GET | 是 | 操作日志列表 |

---

## 安全建议

1. **修改默认密码**：首次使用后请立即修改 `ADMIN_PASSWORD`
2. **保护 .env 文件**：不要将 `.env` 文件提交到版本控制系统
3. **定期查看日志**：通过操作日志监控异常行为
4. **使用强密码**：建议使用包含大小写字母、数字、特殊字符的密码

---

## 数据库变更

管理后台会创建以下数据库表：

- `admin_operation_logs` - 操作日志表
- `users` 表新增 `is_disabled` 字段 - 用户禁用状态

数据库文件位置：`backend/data/users.db`

---

## 故障排除

### 无法登录

1. 检查 `.env` 中的 `ADMIN_PASSWORD` 配置
2. 确认后端服务已启动
3. 检查浏览器控制台是否有错误信息

### 用户列表为空

- 确认已有用户注册
- 检查数据库文件 `backend/data/users.db` 是否存在

### 操作日志不显示

- 确认数据库表 `admin_operation_logs` 已创建
- 首次启动时会自动创建表结构
