-- ============================================
-- 迁移脚本：创建 schema_migrations 元数据表
-- 说明：记录已执行的迁移脚本，确保每个迁移只执行一次
-- ============================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT (datetime('now')),
    checksum TEXT,
    status TEXT DEFAULT 'success'
);

CREATE INDEX IF NOT EXISTS idx_schema_migrations_version ON schema_migrations(version);
