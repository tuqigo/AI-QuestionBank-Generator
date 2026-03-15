"""数据库迁移脚本 - 添加 grade 字段到 users 表

使用方法:
    python migrations/add_grade_column.py

注意：线上环境部署前需执行此迁移脚本
"""

import sqlite3
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__) / "data" / "tixiaobao.db"


def migrate():
    """执行迁移"""
    if not DB_PATH.exists():
        print(f"数据库文件不存在：{DB_PATH}")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # 检查 grade 列是否已存在
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if "grade" in columns:
            print("✓ grade 列已存在，无需迁移")
            return True

        # 添加 grade 列
        conn.execute("ALTER TABLE users ADD COLUMN grade TEXT")
        conn.commit()

        print("✓ 成功添加 grade 列到 users 表")
        return True

    except Exception as e:
        print(f"✗ 迁移失败：{e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
