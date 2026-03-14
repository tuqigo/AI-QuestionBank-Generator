"""OTP 验证码 SQLite 存储"""

import sqlite3
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal

from utils.logger import auth_logger

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


# 验证码用途
OtpPurpose = Literal["register", "reset_password"]


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def generate_code() -> str:
    """生成 6 位数字验证码"""
    return str(random.randint(100000, 999999))


def store_otp(email: str, code: str, purpose: OtpPurpose = "register", expire_minutes: int = 5) -> bool:
    """存储 OTP 验证码"""
    conn = _get_connection()
    try:
        # 使用 UTC 时间
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        expires_at_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')

        # 使同一邮箱同用途的旧验证码失效
        conn.execute(
            "UPDATE otp_codes SET expires_at = datetime('now') WHERE email = ? AND purpose = ? AND expires_at > datetime('now')",
            (email, purpose)
        )
        # 插入新验证码
        conn.execute(
            "INSERT INTO otp_codes (email, code, purpose, expires_at) VALUES (?, ?, ?, ?)",
            (email, code, purpose, expires_at_str)
        )
        conn.commit()
        auth_logger.info(f"OTP 存储成功，email: {email}, purpose: {purpose}")
        return True
    except Exception as e:
        auth_logger.error(f"OTP 存储失败：{e}")
        return False
    finally:
        conn.close()


def verify_otp(email: str, code: str, purpose: OtpPurpose = "register") -> bool:
    """验证 OTP 验证码"""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT code, attempts, expires_at FROM otp_codes WHERE email = ? AND purpose = ? ORDER BY id DESC LIMIT 1",
            (email, purpose)
        )
        row = cursor.fetchone()
        if not row:
            auth_logger.warning(f"OTP 验证失败 - 未找到验证码，email: {email}, purpose: {purpose}")
            return False

        # 检查是否已过期
        expires_at = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S.%f") if "." in row["expires_at"] else datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now(timezone.utc).replace(tzinfo=None) > expires_at:
            auth_logger.warning(f"OTP 验证失败 - 验证码已过期，email: {email}, purpose: {purpose}")
            return False

        # 检查尝试次数
        if row["attempts"] >= 5:
            auth_logger.warning(f"OTP 验证失败 - 尝试次数超限，email: {email}, purpose: {purpose}")
            return False

        # 验证验证码
        if row["code"] != code:
            # 增加尝试次数
            conn.execute(
                "UPDATE otp_codes SET attempts = attempts + 1 WHERE email = ? AND purpose = ? AND code = ?",
                (email, purpose, row["code"])
            )
            conn.commit()
            auth_logger.warning(f"OTP 验证失败 - 验证码错误，email: {email}, purpose: {purpose}, attempts: {row['attempts'] + 1}")
            return False

        # 验证成功，清除验证码
        conn.execute("DELETE FROM otp_codes WHERE email = ? AND purpose = ? AND code = ?", (email, purpose, code))
        conn.commit()
        auth_logger.info(f"OTP 验证成功，email: {email}, purpose: {purpose}")
        return True
    except Exception as e:
        auth_logger.error(f"OTP 验证异常：{e}")
        return False
    finally:
        conn.close()


def check_rate_limit(email: str, purpose: OtpPurpose = "register", ip_address: Optional[str] = None, window_minutes: int = 60, max_requests: int = 5) -> bool:
    """检查速率限制 - 返回 True 表示可以发送，False 表示被限制"""
    conn = _get_connection()
    try:
        # 使用 UTC 时间
        reset_at = datetime.now(timezone.utc) + timedelta(minutes=window_minutes)
        reset_at_str = reset_at.strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.execute(
            "SELECT request_count, reset_at FROM otp_rate_limit WHERE email = ? AND purpose = ? AND ip_address IS ? ORDER BY id DESC LIMIT 1",
            (email, purpose, ip_address)
        )
        row = cursor.fetchone()
        if not row:
            # 首次请求
            conn.execute(
                "INSERT INTO otp_rate_limit (email, purpose, ip_address, reset_at) VALUES (?, ?, ?, ?)",
                (email, purpose, ip_address, reset_at_str)
            )
            conn.commit()
            auth_logger.debug(f"速率限制检查通过 - 首次请求，email: {email}, purpose: {purpose}")
            return True

        # 检查是否需要重置
        reset_time = datetime.strptime(row["reset_at"], "%Y-%m-%d %H:%M:%S.%f") if "." in row["reset_at"] else datetime.strptime(row["reset_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now(timezone.utc).replace(tzinfo=None) > reset_time:
            # 重置计数器
            conn.execute(
                "UPDATE otp_rate_limit SET request_count = 1, reset_at = ? WHERE email = ? AND purpose = ? AND ip_address IS ?",
                (reset_at_str, email, purpose, ip_address)
            )
            conn.commit()
            auth_logger.debug(f"速率限制检查通过 - 已重置，email: {email}, purpose: {purpose}")
            return True

        # 检查请求次数
        if row["request_count"] >= max_requests:
            auth_logger.warning(f"速率限制 - 请求次数超限，email: {email}, purpose: {purpose}, count: {row['request_count']}")
            return False

        # 增加计数
        conn.execute(
            "UPDATE otp_rate_limit SET request_count = request_count + 1 WHERE email = ? AND purpose = ? AND ip_address IS ?",
            (email, purpose, ip_address)
        )
        conn.commit()
        auth_logger.debug(f"速率限制检查通过，email: {email}, purpose: {purpose}, count: {row['request_count'] + 1}")
        return True
    except Exception as e:
        auth_logger.error(f"速率限制检查异常：{e}")
        return True  # 失败时放行
    finally:
        conn.close()


def cleanup_expired():
    """清理过期的 OTP 记录"""
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM otp_codes WHERE expires_at < datetime('now')")
        conn.execute("DELETE FROM otp_rate_limit WHERE reset_at < datetime('now')")
        conn.commit()
        auth_logger.debug("过期 OTP 记录清理完成")
    finally:
        conn.close()
