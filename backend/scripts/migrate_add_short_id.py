"""数据库迁移脚本 - 添加 short_id 列

用法:
    python scripts/migrate_add_short_id.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from utils.logger import setup_logger

logger = setup_logger("migrate")

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def migrate():
    """执行迁移"""
    if not DB_PATH.exists():
        logger.error(f"数据库文件不存在：{DB_PATH}")
        return

    conn = get_connection()
    try:
        # 检查 short_id 列是否已存在
        columns = conn.execute("PRAGMA table_info(user_question_records)").fetchall()
        column_names = [col["name"] for col in columns]

        if "short_id" in column_names:
            logger.info("short_id 列已存在，无需添加")
        else:
            # 添加 short_id 列
            conn.execute("ALTER TABLE user_question_records ADD COLUMN short_id TEXT")
            conn.commit()
            logger.info("short_id 列添加成功")

        # 检查索引是否已存在
        indexes = conn.execute("PRAGMA index_list(user_question_records)").fetchall()
        index_names = [idx["name"] for idx in indexes]

        if "idx_user_question_records_short_id" not in index_names:
            # 创建索引
            conn.execute("""
                CREATE INDEX idx_user_question_records_short_id
                ON user_question_records(short_id)
            """)
            conn.commit()
            logger.info("short_id 索引创建成功")
        else:
            logger.info("short_id 索引已存在")

        logger.info("数据库迁移完成")

    except Exception as e:
        logger.error(f"迁移失败：{e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
