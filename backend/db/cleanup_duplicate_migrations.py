#!/usr/bin/env python3
"""
清理 schema_migrations 表中的重复记录

使用方法：
    python -m db.cleanup_duplicate_migrations

注意：本脚本会在执行前备份当前数据到 JSON 文件
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

from config import DB_PATH


def cleanup_duplicates():
    """清理重复的迁移记录"""

    if not Path(str(DB_PATH)).exists():
        print(f"数据库文件不存在：{DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 检查 schema_migrations 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
    if cursor.fetchone() is None:
        print("schema_migrations 表不存在")
        return

    # 查找重复的版本
    cursor.execute("""
        SELECT version, COUNT(*) as cnt
        FROM schema_migrations
        GROUP BY version
        HAVING cnt > 1
    """)
    duplicates = cursor.fetchall()

    if not duplicates:
        print("没有发现重复的迁移记录")
        return

    print(f"发现 {len(duplicates)} 个重复版本:")
    for dup in duplicates:
        print(f"  - version: {dup['version']}, 重复次数：{dup['cnt']}")

    # 备份当前数据
    backup_file = f"schema_migrations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    cursor.execute("SELECT * FROM schema_migrations ORDER BY id")
    all_records = [dict(row) for row in cursor.fetchall()]

    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"\n已备份所有记录到：{backup_file}")

    # 删除重复记录，只保留每个版本的第一条（最小 id）
    cursor.execute("""
        DELETE FROM schema_migrations
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM schema_migrations
            GROUP BY version
        )
    """)
    deleted_count = cursor.rowcount
    conn.commit()

    print(f"已删除 {deleted_count} 条重复记录")

    # 验证清理结果
    cursor.execute("""
        SELECT version, COUNT(*) as cnt
        FROM schema_migrations
        GROUP BY version
        HAVING cnt > 1
    """)
    remaining_duplicates = cursor.fetchall()

    if remaining_duplicates:
        print(f"警告：仍有 {len(remaining_duplicates)} 个重复版本未清理")
    else:
        print("清理完成，没有重复记录了")

    # 显示清理后的统计
    cursor.execute("SELECT COUNT(*) as total FROM schema_migrations")
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as success FROM schema_migrations WHERE status = 'success'")
    success = cursor.fetchone()['success']
    cursor.execute("SELECT COUNT(*) as failed FROM schema_migrations WHERE status = 'failed'")
    failed = cursor.fetchone()['failed']

    print(f"\n清理后统计:")
    print(f"  总记录数：{total}")
    print(f"  成功：{success}")
    print(f"  失败：{failed}")

    conn.close()


if __name__ == "__main__":
    cleanup_duplicates()
