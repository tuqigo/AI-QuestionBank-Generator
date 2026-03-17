# 数据库迁移系统

## 概述

数据库迁移系统用于管理 SQLite 数据库的结构变更和数据初始化，支持多实例部署场景，确保迁移的幂等性和安全性。

## 核心特性

- **幂等性保证**: 每个迁移脚本只执行一次
- **状态追踪**: 通过 `schema_migrations` 表记录已执行的迁移
- **异常处理**: 迁移失败时记录状态并抛出异常
- **事务支持**: 每个迁移在独立事务中执行，失败自动回滚
- **多实例安全**: 支持 CI/CD 独立执行，避免并发问题

## 文件结构

```
backend/db/
├── __init__.py                 # 数据库初始化（仅执行 schema.sql）
├── migrations/
│   ├── __init__.py             # 迁移管理器核心逻辑
│   ├── cli.py                  # 命令行迁移工具
│   ├── 000_create_schema_migrations_table.sql
│   ├── 001_*.sql               # 增量迁移脚本
│   └── ...
└── MIGRATIONS_GUIDE.md         # 使用指南
```

## 迁移脚本命名规范

```
NNN_description.sql
```

- `NNN`: 3 位数字版本号（001, 002, 003...）
- `description`: 描述性名称，使用下划线分隔

示例：
- `001_add_questions_table.sql` - 题目表结构
- `002_add_question_templates.sql` - 模板系统表

## 使用方法

### 命令行工具

```bash
cd backend

# 查看迁移状态
python -m db.migrations_cli status

# 执行迁移
python -m db.migrations_cli migrate

# 查看待执行的迁移
python -m db.migrations_cli pending

# 查看迁移历史
python -m db.migrations_cli history

# JSON 格式输出（用于程序调用）
python -m db.migrations_cli json
```

### Python API

```python
from db.migrations import MigrationExecutor, get_migration_status

# 执行迁移
executor = MigrationExecutor()
executed = executor.migrate()
print(f"执行了 {len(executed)} 个迁移")

# 获取状态
status = get_migration_status()
print(f"成功：{status['successful']}, 待执行：{status['pending']}")

# 查看待执行的迁移
pending = executor.get_pending_migrations()
print(f"待执行：{pending}")

# 查看迁移历史
history = executor.get_migration_history()
for record in history:
    print(f"{record['version']}: {record['filename']} - {record['status']}")
```

## 编写迁移脚本

### 新增表

```sql
-- 016_add_new_feature_table.sql
CREATE TABLE IF NOT EXISTS new_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_new_features_name
    ON new_features(name);
```

### 修改现有表

```sql
-- 017_add_email_column_to_users.sql
ALTER TABLE users ADD COLUMN email TEXT;
```

### 插入配置数据

```sql
-- 018_add_default_config.sql
INSERT INTO configs (key, value, description)
VALUES ('app_name', '题小宝', '应用名称');
```

## 元数据表结构

`schema_migrations` 表记录迁移执行历史：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| version | TEXT | 版本号（唯一） |
| filename | TEXT | 迁移文件名 |
| executed_at | TIMESTAMP | 执行时间 |
| checksum | TEXT | SQL 内容校验和（SHA-256） |
| status | TEXT | 状态（success/failed） |

## 部署流程

### 开发环境

```bash
# 1. 先执行迁移
python -m db.migrations_cli migrate

# 2. 再启动应用
uvicorn main:app --reload
```

### 生产环境（多实例部署）

```bash
# restart_backend.sh 中的流程

# 1. 拉取代码
git pull

# 2. 代码兼容性检查
python3 -m py_compile main.py

# 3. 执行数据库迁移
python -m db.migrations_cli migrate

# 4. 停止旧服务
kill <old_pid>

# 5. 启动新服务
nohup uvicorn main:app &
```

## 安全特性

### 1. 幂等性保证

通过 `schema_migrations` 表确保每个迁移只执行一次：

```python
# 执行前检查
if version in executed_versions:
    continue  # 跳过已执行的迁移
```

### 2. 事务保护

每个迁移在独立事务中执行：

```python
with conn:  # 自动提交/回滚
    cursor.executescript(sql_content)
```

### 3. 失败标记

失败的迁移会被标记为 `failed` 状态：

```python
# 迁移失败时
cursor.execute("""
    INSERT INTO schema_migrations (version, filename, checksum, status)
    VALUES (?, ?, ?, 'failed')
""", (version, filename, checksum))
```

### 4. 校验和记录

记录 SQL 内容的 SHA-256 校验和，可用于检测篡改。

## 故障排查

### 迁移失败

检查 `schema_migrations` 表中的失败记录：

```sql
SELECT * FROM schema_migrations WHERE status = 'failed';
```

### 手动修复

如果迁移失败导致数据库不一致：

1. 修复 SQL 文件或数据库状态
2. 手动删除失败的迁移记录：
   ```sql
   DELETE FROM schema_migrations WHERE version = '0XX';
   ```
3. 重新执行迁移：`python -m db.migrations_cli migrate`

### 回滚

当前版本暂不支持自动回滚。需要回滚时：

1. 手动编写回滚 SQL
2. 执行回滚 SQL
3. 从 `schema_migrations` 删除对应记录

## 最佳实践

1. **永远不要修改已提交的迁移文件** - 如需修改，创建新的迁移脚本
2. **每次迁移只做一件事** - 保持迁移原子性
3. **使用 IF NOT EXISTS** - 增强迁移的健壮性
4. **测试迁移脚本** - 在测试环境验证后再应用到生产
5. **备份数据库** - 执行迁移前备份重要数据

## 多实例部署说明

### 为什么需要独立执行迁移

在多实例部署场景下，如果每个实例启动时都自动执行迁移，可能导致：

1. **并发锁竞争** - 多个实例同时写 `schema_migrations` 表
2. **资源浪费** - 重复检查、重复执行
3. **故障风险** - 一个实例迁移失败影响其他实例

### 解决方案

1. **CI/CD 阶段独立执行** - 部署前在单一节点执行迁移
2. **应用启动时不自动执行** - `main.py` 中移除了自动调用
3. **迁移失败时阻止部署** - `restart_backend.sh` 中检查迁移状态

## 相关文档

- [后端代码结构](./backend-code-structure.md) - 数据库操作章节
- [后端系统架构](./backend-system-architecture.md) - 数据存储层
- [重启脚本使用说明](../restart_backend.sh)
