"""NanoID 短 ID 生成工具

生成 12 字符的 URL 安全短 ID，用于替代数据库自增 ID 对外暴露
使用 Python 标准库 secrets 和 base64，无需额外依赖，兼容 Python 3.8+
"""

import secrets
import string

# 使用 URL 安全的字符集：A-Za-z0-9
# 12 字符长度，碰撞概率极低（约 1/10^21）
SHORT_ID_LENGTH = 12

# URL 安全字符集（去掉 - 和_，只用字母数字，更简洁）
ALPHABET = string.ascii_letters + string.digits


def generate_short_id() -> str:
    """生成一个短 ID

    Returns:
        12 字符的随机 ID，例如：nX7kP9mQ2aB3
    """
    return ''.join(secrets.choice(ALPHABET) for _ in range(SHORT_ID_LENGTH))


def generate_unique_short_id(conn) -> str:
    """生成唯一的短 ID（如果冲突则重新生成）

    Args:
        conn: SQLite 数据库连接

    Returns:
        唯一的短 ID
    """
    max_attempts = 10
    for _ in range(max_attempts):
        short_id = generate_short_id()
        # 检查是否已存在
        row = conn.execute(
            "SELECT 1 FROM user_question_records WHERE short_id = ?",
            (short_id,)
        ).fetchone()
        if not row:
            return short_id
    # 如果多次尝试后仍冲突，抛出异常
    raise RuntimeError("生成短 ID 失败：多次尝试后仍冲突")
