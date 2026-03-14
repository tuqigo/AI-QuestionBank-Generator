# 数据库路径配置重构

## 问题

之前每个文件都重复定义数据库路径：
```python
# 6 个文件都有这段重复代码
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"
# 或
DB_PATH = Path(__file__).parent.parent.parent / "data" / "users.db"
```

**问题**：
1. 代码重复（DRY 原则被违反）
2. 路径计算复杂，容易出错
3. 文件移动时需要更新路径逻辑
4. 维护成本高

## 解决方案

在 `config.py` 中统一配置：

```python
# config.py
from pathlib import Path

BASE_DIR = Path(__file__).parent  # backend/ 目录
DB_PATH = BASE_DIR / "data" / "users.db"
```

所有文件使用统一配置：

```python
from config import DB_PATH
```

## 修改的文件

| 文件 | 修改前 | 修改后 |
|------|--------|--------|
| `config.py` | 无 DB_PATH 配置 | 新增 `DB_PATH = BASE_DIR / "data" / "users.db"` |
| `services/user/user_store.py` | 6 行路径计算代码 | 1 行导入 |
| `services/question/question_store.py` | 6 行路径计算代码 | 1 行导入 |
| `services/question/question_record_store.py` | 6 行路径计算代码 | 1 行导入 |
| `services/question/ai_generation_record_store.py` | 6 行路径计算代码 | 1 行导入 |
| `services/admin/admin_operation_log.py` | 6 行路径计算代码 | 1 行导入 |
| `models/otp.py` | 6 行路径计算代码 | 1 行导入 |
| `db/__init__.py` | 独立路径计算 | 从 config 导入 |

## 代码减少统计

- 删除重复代码：约 **42 行**
- 新增代码：**3 行**（config.py 中的配置）
- 净减少：**39 行**

## 优势

1. **单一职责**：路径配置只在一个地方管理
2. **易于维护**：修改数据库位置只需改一处
3. **不易出错**：无需计算 `parent.parent.parent...`
4. **代码清晰**：导入即用，意图明确

## 使用示例

```python
# 任何需要数据库连接的文件
from config import DB_PATH

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

## 扩展性

未来如需支持多数据库或切换数据库位置：

```python
# config.py
DB_PATH = os.getenv("DB_PATH", BASE_DIR / "data" / "users.db")
# 或通过环境变量配置
```

无需修改任何业务代码。
