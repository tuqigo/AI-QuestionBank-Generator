"""
补全已执行的迁移记录

使用场景：
- 线上数据库已经执行过某些迁移 SQL，但 schema_migrations 表中没有记录
- 执行此脚本后，迁移系统会认为这些迁移已执行，避免重复执行

使用方法：
    python3 sync_migration_records.py
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime

# 迁移文件目录
MIGRATIONS_DIR = Path(__file__).parent / "db" / "migrations"

# 数据库路径（根据实际情况修改）
DB_PATH = Path(__file__).parent / "data" / "tixiaobao.db"


def calculate_checksum(content: str) -> str:
    """计算 SQL 内容的 SHA-256 校验和"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def sync_migration_records(db_path: str = None):
    """
    补全迁移记录

    读取 migrations 目录中的所有 SQL 文件，
    将已存在的表/数据对应的迁移记录插入到 schema_migrations 表中
    """
    db_path = db_path or DB_PATH

    if not db_path.exists():
        print(f"数据库文件不存在：{db_path}")
        print("如果是全新数据库，无需执行此脚本，直接运行迁移即可")
        return

    # 连接数据库
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 第一步：确保 schema_migrations 表存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT (datetime('now')),
                checksum TEXT,
                status TEXT DEFAULT 'success'
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_version
            ON schema_migrations(version)
        """)
        conn.commit()
        print("OK schema_migrations 表已创建/存在")

        # 第二步：获取当前已存在的迁移记录
        cursor.execute("SELECT version, filename FROM schema_migrations ORDER BY version")
        existing_records = {row[0]: row[1] for row in cursor.fetchall()}
        print(f"OK 当前已有 {len(existing_records)} 条迁移记录")

        # 第三步：获取所有迁移文件
        if not MIGRATIONS_DIR.exists():
            print(f"迁移目录不存在：{MIGRATIONS_DIR}")
            return

        migration_files = sorted([f for f in MIGRATIONS_DIR.glob("*.sql")])
        print(f"OK 发现 {len(migration_files)} 个迁移文件")

        # 第四步：补全缺失的记录
        added_count = 0
        skipped_count = len(existing_records)

        for filepath in migration_files:
            filename = filepath.name
            version = filename[:3]  # 提取版本号，如 "001"

            # 如果已有记录，跳过
            if version in existing_records:
                print(f"  - 跳过：{filename} (已存在记录)")
                continue

            # 读取文件内容并计算校验和
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            checksum = calculate_checksum(content)

            # 插入记录
            cursor.execute("""
                INSERT INTO schema_migrations (version, filename, checksum, status)
                VALUES (?, ?, ?, 'success')
            """, (version, filename, checksum))

            added_count += 1
            print(f"  + 添加：{filename}")

        # 提交事务
        conn.commit()

        # 输出结果
        print("\n" + "=" * 50)
        print(f"迁移记录同步完成")
        print(f"  新增：{added_count} 条")
        print(f"  跳过：{skipped_count} 条")
        print(f"  总计：{added_count + skipped_count} 条")
        print("=" * 50)

        # 验证：显示所有记录
        cursor.execute("SELECT version, filename, status FROM schema_migrations ORDER BY version")
        print("\n当前所有迁移记录:")
        for row in cursor.fetchall():
            print(f"  {row[0]} | {row[1]} | {row[2]}")

    except Exception as e:
        print(f"错误：{e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    # 支持命令行指定数据库路径
    db_path = sys.argv[1] if len(sys.argv) > 1 else None

    if db_path:
        print(f"使用指定的数据库路径：{db_path}")

    sync_migration_records(db_path)
