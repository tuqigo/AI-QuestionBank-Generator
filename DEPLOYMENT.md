# 用户年级选择功能 - 部署说明

## 功能说明

注册成功后弹出年级选择器，用户选择孩子年级后保存到数据库。

年级选项：
- 小学：一年级 ~ 六年级（grade1~grade6）
- 初中：初一 ~ 初三（grade7~grade9）

---

## 部署步骤

### 1. 数据库迁移（必须先执行）

```bash
cd backend
python migrations/add_grade_column.py
```

验证迁移成功：
```bash
# Linux/Mac
sqlite3 data/tixiaobao.db "PRAGMA table_info(users);"

# Windows
python -c "import sqlite3; conn=sqlite3.connect('data/tixiaobao.db'); print([r for r in conn.execute('PRAGMA table_info(users)')])"
```

输出应包含 `grade` 字段。

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

---

## API 接口

### 更新用户年级
```http
PUT /api/users/grade
Authorization: Bearer <token>
Content-Type: application/json

{
  "grade": "grade1"  // grade1~grade9
}
```

### 获取用户信息（含年级）
```http
GET /api/auth/me
Authorization: Bearer <token>
```

响应：
```json
{
  "email": "user@example.com",
  "grade": "grade1"
}
```

---

## 前端测试流程

1. 打开浏览器访问 http://localhost:5173
2. 点击"立即注册"
3. 输入邮箱、密码，获取并填写验证码
4. 点击"注册"按钮
5. **注册成功后应自动弹出年级选择器**
6. 选择一个年级（如"一年级"）
7. 提示"年级设置成功"后自动跳转到工作台

---

## 文件变更清单

### 后端
- `backend/db/schema.sql` - 添加 grade 字段
- `backend/models/user.py` - 添加 UserGradeUpdate 模型
- `backend/services/user/user_store.py` - 添加 update_user_grade 方法
- `backend/api/v1/auth.py` - /me 接口返回 grade
- `backend/api/v1/users.py` - 新增年级更新接口
- `backend/api/v1/__init__.py` - 导出 users_router
- `backend/main.py` - 注册 users 路由
- `backend/migrations/add_grade_column.py` - 迁移脚本（新增）

### 前端
- `frontend/src/components/GradeSelectorModal.tsx` - 年级选择器组件（新增）
- `frontend/src/components/GradeSelectorModal.css` - 样式文件（新增）
- `frontend/src/features/auth/LoginPage.tsx` - 注册成功后弹窗
- `frontend/src/types/index.ts` - 添加 User 类型

---

## 常见问题

### Q: 注册成功后没有弹出年级选择器？
A: 检查浏览器控制台是否有 JavaScript 错误，确认 `getToken` 已正确导入。

### Q: 更新年级失败？
A: 确认后端 `PUT /api/users/grade` 接口可访问，token 有效。

### Q: 线上部署需要注意什么？
A: **必须先执行数据库迁移脚本**，否则会报 "no such column: grade" 错误。
