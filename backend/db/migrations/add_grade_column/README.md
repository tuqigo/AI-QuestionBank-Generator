# 数据库迁移说明

## 执行迁移脚本

部署到线上环境前，**必须先执行数据库迁移脚本**：

```bash
cd backend
python migrations/add_grade_column.py
```

## 迁移内容

- 向 `users` 表添加 `grade` 字段（TEXT 类型）
- 用于存储用户选择的年级（grade1~grade9）

## 验证迁移是否成功

```bash
sqlite3 data/tixiaobao.db "PRAGMA table_info(users);"
```

输出应包含 `grade` 列。
