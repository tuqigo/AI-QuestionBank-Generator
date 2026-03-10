"""管理员操作日志服务"""
import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

from utils.logger import api_logger

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    """初始化操作日志表"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admin_operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator TEXT NOT NULL,
                action TEXT NOT NULL,
                target_type TEXT,
                target_id INTEGER,
                ip TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_logs_action
            ON admin_operation_logs(action, created_at DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_logs_target
            ON admin_operation_logs(target_type, target_id)
        """)
        conn.commit()
        api_logger.info("管理员操作日志表初始化完成")
    except Exception as e:
        api_logger.error(f"初始化操作日志表失败：{e}")
        raise
    finally:
        conn.close()


# 启动时初始化
_init_db()


def log_operation(
    operator: str,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    ip: Optional[str] = None,
    details: Optional[str] = None
) -> int:
    """记录操作日志，返回日志 ID"""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO admin_operation_logs
            (operator, action, target_type, target_id, ip, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (operator, action, target_type, target_id, ip, details)
        )
        conn.commit()
        log_id = cursor.lastrowid
        api_logger.info(f"操作日志记录成功：id={log_id}, action={action}")
        return log_id
    except Exception as e:
        api_logger.error(f"记录操作日志失败：{e}")
        return -1
    finally:
        conn.close()


def get_operation_logs(
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[dict], int, bool]:
    """获取操作日志列表（分页）
    返回：(日志列表，总数，是否有更多)
    """
    conn = _get_connection()
    try:
        # 计算总数
        count_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM admin_operation_logs"
        ).fetchone()
        total = count_row["cnt"] if count_row else 0

        # 分页查询
        offset = (page - 1) * page_size
        rows = conn.execute(
            """
            SELECT id, operator, action, target_type, target_id, ip, created_at
            FROM admin_operation_logs
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (page_size, offset)
        ).fetchall()

        logs = []
        for row in rows:
            logs.append({
                "id": row["id"],
                "operator": row["operator"],
                "action": row["action"],
                "target_type": row["target_type"],
                "target_id": row["target_id"],
                "ip": row["ip"],
                "created_at": row["created_at"]
            })

        has_more = offset + len(rows) < total

        return logs, total, has_more
    except Exception as e:
        api_logger.error(f"获取操作日志失败：{e}")
        return [], 0, False
    finally:
        conn.close()


def get_logs_by_target(
    target_type: str,
    target_id: int
) -> List[dict]:
    """根据操作对象查询日志"""
    conn = _get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, operator, action, target_type, target_id, ip, created_at
            FROM admin_operation_logs
            WHERE target_type = ? AND target_id = ?
            ORDER BY id DESC
            """,
            (target_type, target_id)
        ).fetchall()

        logs = []
        for row in rows:
            logs.append({
                "id": row["id"],
                "operator": row["operator"],
                "action": row["action"],
                "target_type": row["target_type"],
                "target_id": row["target_id"],
                "ip": row["ip"],
                "created_at": row["created_at"]
            })
        return logs
    except Exception as e:
        api_logger.error(f"查询目标日志失败：{e}")
        return []
    finally:
        conn.close()
