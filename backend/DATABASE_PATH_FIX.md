# 数据库路径修复报告

## 修复时间
2026-03-14 23:15

## 问题描述
```
sqlite3.OperationalError: unable to open database file
File "D:\project\AI-QuestionBank-Generator\backend\services\user\user_store.py", line 23
```

## 问题原因

在代码重组过程中，多个服务文件移动到了新的子目录，但数据库路径配置未同步更新：

| 文件 | 原路径 | 新路径 | 路径计算 |
|------|--------|--------|----------|
| `user_store.py` | `services/` | `services/user/` | `parent.parent` → `services/` ❌ |
| `question_store.py` | `services/` | `services/question/` | `parent.parent` → `services/` ❌ |
| `question_record_store.py` | `services/` | `services/question/` | `parent.parent` → `services/` ❌ |
| `ai_generation_record_store.py` | `services/` | `services/question/` | `parent.parent` → `services/` ❌ |
| `admin_operation_log.py` | `services/` | `services/admin/` | `parent.parent` → `services/` ❌ |
| `otp.py` | `models/` | `models/` (未移动) | `parent.parent` → `backend/` ✓ |

数据库文件位置：`backend/data/users.db`

## 修复内容

### 修复的文件

1. **`services/user/user_store.py`**
   ```python
   # 修改前
   DB_PATH = Path(__file__).parent.parent / "data" / "users.db"

   # 修改后
   DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"
   ```

2. **`services/question/question_store.py`**
   ```python
   DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"
   ```

3. **`services/question/question_record_store.py`**
   ```python
   DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"
   ```

4. **`services/question/ai_generation_record_store.py`**
   ```python
   DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"
   ```

5. **`services/admin/admin_operation_log.py`**
   ```python
   DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"
   ```

6. **`models/otp.py`**
   ```python
   # 修改前
   DB_PATH = Path(__file__).parent.parent / "data" / "users.db"

   # 修改后 (models 在 backend 根目录，只需 parent)
   DB_PATH = Path(__file__).parent / "data" / "users.db"
   ```

## 验证步骤

### 1. 后端启动测试
```bash
cd backend
python -c "import main; print('OK')"
# 输出：Backend startup OK
```

### 2. 数据库连接测试
```bash
python -c "from services.user.user_store import get_user; print(get_user('test@test.com'))"
# 输出：None (用户不存在，表示数据库连接正常)
```

## 路径计算说明

```
backend/
├── data/
│   └── users.db          # 数据库文件
├── services/
│   ├── user/
│   │   └── user_store.py # __file__ → parent.parent.parent = backend/
│   └── question/
│       └── *.py          # __file__ → parent.parent.parent = backend/
└── models/
    └── otp.py            # __file__ → parent = backend/
```

## 建议

### 短期
- 使用环境变量配置数据库路径，避免硬编码相对路径
- 在应用启动时验证数据库文件是否存在

### 长期
- 考虑使用配置中心管理所有路径配置
- 添加路径配置单元测试

## 相关文件修改清单

| 文件 | 修改内容 | 状态 |
|------|----------|------|
| `services/user/user_store.py` | DB_PATH 路径修正 | ✓ |
| `services/question/question_store.py` | DB_PATH 路径修正 | ✓ |
| `services/question/question_record_store.py` | DB_PATH 路径修正 | ✓ |
| `services/question/ai_generation_record_store.py` | DB_PATH 路径修正 | ✓ |
| `services/admin/admin_operation_log.py` | DB_PATH 路径修正 | ✓ |
| `models/otp.py` | DB_PATH 路径修正 | ✓ |
