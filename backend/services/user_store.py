"""SQLite 用户存储"""

import sqlite3
from pathlib import Path
from typing import Optional

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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
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

        # 插入新用户 - 支持空密码
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
