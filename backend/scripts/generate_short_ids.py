"""为现有历史记录生成 short_id

用法:
    python scripts/generate_short_ids.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from utils.short_id import generate_short_id
from utils.logger import setup_logger

logger = setup_logger("migrate")

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_short_id_exists(conn: sqlite3.Connection, short_id: str) -> bool:
    """检查 short_id 是否已存在"""
    row = conn.execute(
        "SELECT 1 FROM user_question_records WHERE short_id = ?",
        (short_id,)
    ).fetchone()
    return row is not None


def generate_unique_short_id(conn: sqlite3.Connection) -> str:
    """生成唯一的 short_id"""
    max_attempts = 10
    for _ in range(max_attempts):
        short_id = generate_short_id()
        if not check_short_id_exists(conn, short_id):
            return short_id
    raise RuntimeError("生成 short_id 失败：多次尝试后仍冲突")


def migrate():
    """执行迁移"""
    if not DB_PATH.exists():
        logger.error(f"数据库文件不存在：{DB_PATH}")
        return

    conn = get_connection()
    try:
        # 查询所有没有 short_id 的记录
        rows = conn.execute("""
            SELECT id, short_id FROM user_question_records
            WHERE short_id IS NULL OR short_id = ''
        """).fetchall()

        if not rows:
            logger.info("所有记录已有 short_id，无需迁移")
            return

        total = len(rows)
        logger.info(f"找到 {total} 条需要生成 short_id 的记录")

        success_count = 0
        error_count = 0

        for i, row in enumerate(rows):
            record_id = row["id"]
            try:
                short_id = generate_unique_short_id(conn)
                conn.execute(
                    "UPDATE user_question_records SET short_id = ? WHERE id = ?",
                    (short_id, record_id)
                )
                conn.commit()
                success_count += 1

                if (i + 1) % 100 == 0 or (i + 1) == total:
                    logger.info(f"进度：{i + 1}/{total} ({(i + 1) / total * 100:.1f}%)")

            except Exception as e:
                error_count += 1
                logger.error(f"处理记录 {record_id} 失败：{e}")

        logger.info(f"迁移完成！成功：{success_count}, 失败：{error_count}")

    except Exception as e:
        logger.error(f"迁移失败：{e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
