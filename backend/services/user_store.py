"""SQLite 用户存储"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple

from models.user import UserInDB
from services.auth import get_password_hash
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
        # 创建表（如果不存在）
        # 使用 datetime('now') 存储 UTC 时间（SQLite 默认行为）
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT (datetime('now')),
                is_disabled INTEGER DEFAULT 0
            )
        """)
        # 检查是否需要添加 is_disabled 列（兼容已有数据库）
        try:
            conn.execute("ALTER TABLE users ADD COLUMN is_disabled INTEGER DEFAULT 0")
            conn.commit()
            user_logger.info("为用户表添加 is_disabled 列成功")
        except Exception:
            # 列已存在，忽略
            pass
        conn.commit()
        user_logger.info("数据库表初始化完成")
    finally:
        conn.close()


# 启动时初始化数据库
_init_db()


def get_user(email: str) -> Optional[UserInDB]:
    """根据邮箱查询用户"""
    user_logger.info(f"查询用户：{email}")
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user_logger.info(f"用户存在：{email}")
            return UserInDB(
                id=row["id"],
                email=row["email"],
                hashed_password=row["hashed_password"]
            )
        else:
            user_logger.warning(f"用户不存在：{email}")
            return None
    finally:
        conn.close()


def create_user(email: str, password: str = "") -> UserInDB:
    """创建新用户"""
    user_logger.info(f"创建新用户：{email}")
    conn = _get_connection()
    try:
        # 检查用户是否已存在
        cursor = conn.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            user_logger.warning(f"用户已存在：{email}")
            raise ValueError("邮箱已被注册")

        # 插入新用户 - 使用数据库默认的 UTC 时间
        if password:
            hashed = get_password_hash(password)
        else:
            hashed = ""
        cursor = conn.execute(
            "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
            (email, hashed)
        )
        conn.commit()
        user_logger.info(f"用户创建成功：{email}")
        return UserInDB(
            id=cursor.lastrowid,
            email=email,
            hashed_password=hashed
        )
    finally:
        conn.close()


def update_password(email: str, new_password: str) -> bool:
    """更新用户密码"""
    user_logger.info(f"更新用户密码：{email}")
    conn = _get_connection()
    try:
        # 检查用户是否存在
        cursor = conn.execute("SELECT email FROM users WHERE email = ?", (email,))
        if not cursor.fetchone():
            user_logger.warning(f"用户不存在：{email}")
            raise ValueError("用户不存在")

        # 更新密码
        hashed = get_password_hash(new_password)
        conn.execute(
            "UPDATE users SET hashed_password = ? WHERE email = ?",
            (hashed, email)
        )
        conn.commit()
        user_logger.info(f"用户密码更新成功：{email}")
        return True
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """根据 ID 查询用户"""
    user_logger.info(f"根据 ID 查询用户：{user_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT id, email, hashed_password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            user_logger.info(f"用户存在：ID={user_id}")
            return UserInDB(
                id=row["id"],
                email=row["email"],
                hashed_password=row["hashed_password"]
            )
        else:
            user_logger.warning(f"用户不存在：ID={user_id}")
            return None
    finally:
        conn.close()


def get_user_by_id_with_status(user_id: int) -> Optional[dict]:
    """根据 ID 查询用户（含状态）"""
    user_logger.info(f"根据 ID 查询用户（含状态）：{user_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, email, created_at, is_disabled FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            user_logger.info(f"用户存在：ID={user_id}")
            return {
                "id": row["id"],
                "email": row["email"],
                "created_at": row["created_at"],
                "is_disabled": bool(row["is_disabled"])
            }
        else:
            user_logger.warning(f"用户不存在：ID={user_id}")
            return None
    finally:
        conn.close()


def get_all_users(
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[dict], int, bool]:
    """获取所有用户列表（分页）
    返回：(用户列表，总数，是否有更多)
    """
    user_logger.info(f"获取用户列表：page={page}, page_size={page_size}")
    conn = _get_connection()
    try:
        # 计算总数
        count_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM users"
        ).fetchone()
        total = count_row["cnt"] if count_row else 0

        # 分页查询
        offset = (page - 1) * page_size
        rows = conn.execute(
            """
            SELECT id, email, created_at, is_disabled
            FROM users
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (page_size, offset)
        ).fetchall()

        users = []
        for row in rows:
            users.append({
                "id": row["id"],
                "email": row["email"],
                "created_at": row["created_at"],
                "is_disabled": bool(row["is_disabled"])
            })

        has_more = offset + len(rows) < total

        return users, total, has_more
    except Exception as e:
        user_logger.error(f"获取用户列表失败：{e}")
        return [], 0, False
    finally:
        conn.close()


def set_user_disabled(user_id: int, is_disabled: bool) -> bool:
    """设置用户禁用状态"""
    user_logger.info(f"设置用户禁用状态：user_id={user_id}, is_disabled={is_disabled}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "UPDATE users SET is_disabled = ? WHERE id = ?",
            (1 if is_disabled else 0, user_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            user_logger.info(f"用户状态更新成功：user_id={user_id}")
            return True
        else:
            user_logger.warning(f"用户不存在：user_id={user_id}")
            return False
    except Exception as e:
        user_logger.error(f"更新用户状态失败：{e}")
        return False
    finally:
        conn.close()
