# 数据库迁移系统使用指南

## 概述

本系统实现 SQLite 数据库的迁移管理，核心特性：

- **幂等性保证**: 每个迁移脚本只执行一次
- **状态追踪**: 通过 `schema_migrations` 表记录已执行的迁移
- **异常处理**: 迁移失败时记录状态并抛出异常
- **事务支持**: 每个迁移在独立事务中执行

**注意**: 迁移不再自动执行，需手动运行 `python -m db.migrations_cli migrate`

## 文件结构

```
backend/db/
├── __init__.py              # 数据库初始化入口
├── migrations/
│   ├── __init__.py          # 迁移管理器核心逻辑
│   ├── cli.py               # 命令行管理工具
│   ├── 000_create_schema_migrations_table.sql  # 迁移表定义
│   ├── 001_*.sql            # 增量迁移脚本
│   └── ...
```

## 迁移脚本命名规范

```
NNN_description.sql
```

- `NNN`: 3 位数字版本号（001, 002, 003...）
- `description`: 描述性名称，使用下划线分隔

示例：
- `001_add_questions_table.sql`
- `002_add_question_templates.sql`

## 使用方法

### 1. 命令行工具

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

### 2. 应用启动前执行迁移

```bash
# 先执行迁移
python -m db.migrations_cli migrate

# 再启动应用
python -m uvicorn main:app --reload
```

### 3. CI/CD 部署流程

```yaml
# 示例：GitHub Actions
- name: Run database migrations
  run: python -m db.migrations_cli migrate

- name: Deploy application
  run: docker-compose up -d
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
| id | INTEGER | 主键 |
| version | TEXT | 版本号（唯一） |
| filename | TEXT | 迁移文件名 |
| executed_at | TIMESTAMP | 执行时间 |
| checksum | TEXT | SQL 内容校验和 |
| status | TEXT | 状态（success/failed） |

## 安全特性

1. **幂等性**: 通过 `schema_migrations` 表确保每个迁移只执行一次
2. **事务保护**: 每个迁移在独立事务中执行，失败自动回滚
3. **校验和**: 记录 SQL 内容校验和，可用于检测篡改
4. **失败标记**: 失败的迁移会被标记为 `failed` 状态

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
