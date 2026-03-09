"""SQLite 用户题目记录存储"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

from models.question_record import QuestionRecordCreate, QuestionRecordResponse
from utils.logger import user_logger

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    """初始化数据库表"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _get_connection()
    try:
        # 创建用户题目记录表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_question_records (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                title           VARCHAR(200) NOT NULL,
                prompt_type     VARCHAR(10) NOT NULL,
                prompt_content  TEXT NOT NULL,
                image_path      VARCHAR(500),
                ai_response     TEXT NOT NULL,
                share_token     VARCHAR(64) UNIQUE,
                is_deleted      INTEGER DEFAULT 0,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 创建索引
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_question_records_user_deleted
            ON user_question_records(user_id, is_deleted, created_at DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_question_records_share_token
            ON user_question_records(share_token)
        """)
        conn.commit()
        user_logger.info("用户题目记录表初始化完成")
    except Exception as e:
        user_logger.error(f"初始化数据库表失败：{e}")
        raise
    finally:
        conn.close()


# 启动时初始化数据库
_init_db()


def create_record(user_id: int, record: QuestionRecordCreate) -> int:
    """创建题目记录，返回新记录的 ID"""
    user_logger.info(f"创建题目记录：user_id={user_id}, title={record.title[:50]}...")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO user_question_records
            (user_id, title, prompt_type, prompt_content, image_path, ai_response)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, record.title, record.prompt_type, record.prompt_content,
             record.image_path, record.ai_response)
        )
        conn.commit()
        record_id = cursor.lastrowid
        user_logger.info(f"题目记录创建成功：id={record_id}")
        return record_id
    except Exception as e:
        user_logger.error(f"创建题目记录失败：{e}")
        raise


def get_record_by_id(record_id: int, user_id: Optional[int] = None) -> Optional[QuestionRecordResponse]:
    """根据 ID 获取记录
    user_id 用于权限校验，为 None 时不校验（用于分享场景）
    """
    user_logger.info(f"获取题目记录：id={record_id}, user_id={user_id}")
    conn = _get_connection()
    try:
        if user_id:
            cursor = conn.execute(
                """
                SELECT id, title, prompt_type, prompt_content, image_path,
                       ai_response, is_deleted, created_at
                FROM user_question_records
                WHERE id = ? AND user_id = ? AND is_deleted = 0
                """,
                (record_id, user_id)
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, title, prompt_type, prompt_content, image_path,
                       ai_response, is_deleted, created_at
                FROM user_question_records
                WHERE id = ? AND is_deleted = 0
                """,
                (record_id,)
            )
        row = cursor.fetchone()
        if row:
            return _row_to_response(row)
        return None
    finally:
        conn.close()


def get_record_by_share_token(share_token: str) -> Optional[QuestionRecordResponse]:
    """通过分享 token 获取记录"""
    user_logger.info(f"通过分享 token 获取记录：token={share_token[:20]}...")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, title, prompt_type, prompt_content, image_path,
                   ai_response, is_deleted, created_at
            FROM user_question_records
            WHERE share_token = ? AND is_deleted = 0
            """,
            (share_token,)
        )
        row = cursor.fetchone()
        if row:
            return _row_to_response(row)
        return None
    finally:
        conn.close()


def get_user_records(
    user_id: int,
    cursor: Optional[int] = None,
    limit: int = 20
) -> Tuple[List[QuestionRecordResponse], Optional[int], bool]:
    """获取用户的题目记录列表（游标分页）
    返回：(记录列表，下一个 cursor, 是否还有更多)
    """
    user_logger.info(f"获取用户记录列表：user_id={user_id}, cursor={cursor}, limit={limit}")
    conn = _get_connection()
    try:
        # 游标分页：查询 cursor 之前的记录（因为 ID 递减）
        if cursor:
            rows = conn.execute(
                """
                SELECT id, title, prompt_type, prompt_content, image_path,
                       ai_response, is_deleted, created_at
                FROM user_question_records
                WHERE user_id = ? AND is_deleted = 0 AND id < ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, cursor, limit)
            )
        else:
            rows = conn.execute(
                """
                SELECT id, title, prompt_type, prompt_content, image_path,
                       ai_response, is_deleted, created_at
                FROM user_question_records
                WHERE user_id = ? AND is_deleted = 0
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit + 1)  # 多查一条判断是否有更多
            )

        results = []
        for row in rows:
            results.append(_row_to_response(row))

        # 判断是否有更多
        has_more = False
        next_cursor = None
        if len(results) > limit:
            has_more = True
            results = results[:limit]  # 去掉多查的那条

        if results:
            next_cursor = results[-1].id

        return results, next_cursor, has_more
    finally:
        conn.close()


def soft_delete_record(record_id: int, user_id: int) -> bool:
    """软删除记录"""
    user_logger.info(f"软删除记录：id={record_id}, user_id={user_id}")
    conn = _get_connection()
    try:
        # 只删除用户自己的记录
        cursor = conn.execute(
            "UPDATE user_question_records SET is_deleted = 1 WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            user_logger.info(f"记录软删除成功：id={record_id}")
            return True
        else:
            user_logger.warning(f"记录软删除失败：记录不存在或无权限 id={record_id}")
            return False
    except Exception as e:
        user_logger.error(f"软删除记录失败：{e}")
        raise


def generate_share_token(record_id: int, user_id: int) -> Optional[str]:
    """生成分享 token
    如果已有 token 则返回现有 token
    """
    user_logger.info(f"生成分享 token: id={record_id}, user_id={user_id}")
    conn = _get_connection()
    try:
        # 先检查是否已有 token
        row = conn.execute(
            "SELECT share_token FROM user_question_records WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        ).fetchone()

        if row and row["share_token"]:
            user_logger.info(f"记录已有分享 token")
            return row["share_token"]

        # 生成新 token（使用简单的随机字符串）
        import secrets
        token = secrets.token_urlsafe(32)

        conn.execute(
            "UPDATE user_question_records SET share_token = ? WHERE id = ? AND user_id = ?",
            (token, record_id, user_id)
        )
        conn.commit()

        user_logger.info(f"分享 token 生成成功")
        return token
    except Exception as e:
        user_logger.error(f"生成分享 token 失败：{e}")
        return None


def get_user_record_count(user_id: int) -> int:
    """获取用户的记录总数（用于限制检查）"""
    user_logger.info(f"获取用户记录总数：user_id={user_id}")
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as count FROM user_question_records WHERE user_id = ? AND is_deleted = 0",
            (user_id,)
        ).fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def delete_oldest_record(user_id: int) -> bool:
    """删除用户最早的一条记录（用于 FIFO 限制）"""
    user_logger.info(f"删除用户最早的记录：user_id={user_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE user_question_records
            SET is_deleted = 1
            WHERE id = (
                SELECT id FROM user_question_records
                WHERE user_id = ? AND is_deleted = 0
                ORDER BY created_at ASC
                LIMIT 1
            )
            """,
            (user_id,)
        )
        conn.commit()
        if cursor.rowcount > 0:
            user_logger.info(f"最早记录软删除成功")
            return True
        return False
    except Exception as e:
        user_logger.error(f"删除最早记录失败：{e}")
        return False


def _row_to_response(row: sqlite3.Row) -> QuestionRecordResponse:
    """将数据库行转换为响应对象"""
    return QuestionRecordResponse(
        id=row["id"],
        title=row["title"],
        prompt_type=row["prompt_type"],
        prompt_content=row["prompt_content"],
        image_path=row["image_path"],
        ai_response=row["ai_response"],
        is_deleted=bool(row["is_deleted"]),
        created_at=row["created_at"]
    )
