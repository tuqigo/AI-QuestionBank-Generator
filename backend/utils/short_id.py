"""NanoID 短 ID 生成工具

生成 12 字符的 URL 安全短 ID，用于替代数据库自增 ID 对外暴露
"""

from nanoid import generate

# 使用 URL 安全的字符集：A-Za-z0-9_-
# 12 字符长度，碰撞概率极低（约 1/10^21）
SHORT_ID_LENGTH = 12


def generate_short_id() -> str:
    """生成一个短 ID

    Returns:
        12 字符的 NanoID，例如：nX7kP9mQ2aB3
    """
    return generate(size=SHORT_ID_LENGTH)


def generate_unique_short_id(check_func) -> str:
    """生成唯一的短 ID（如果冲突则重新生成）

    Args:
        check_func: 检查 ID 是否已存在的函数，接收 short_id 参数，返回 bool

    Returns:
        唯一的短 ID
    """
    max_attempts = 10
    for _ in range(max_attempts):
        short_id = generate_short_id()
        if not check_func(short_id):
            return short_id
    # 如果多次尝试后仍冲突，抛出异常
    raise RuntimeError(f"生成短 ID 失败：多次尝试后仍冲突")
