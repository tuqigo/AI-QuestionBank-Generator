"""管理员认证服务"""
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import bcrypt

from config import JWT_SECRET, JWT_ALGORITHM
from utils.logger import auth_logger

# 管理员密码哈希存储
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
if not ADMIN_PASSWORD_HASH:
    # 首次运行时生成默认哈希（实际应通过 .env 配置）
    # 默认密码：admin123
    ADMIN_PASSWORD_HASH = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    auth_logger.warning("使用默认管理员密码哈希（admin123），生产环境请配置 ADMIN_PASSWORD_HASH 环境变量")

# 管理员 Token 有效期（2 小时）
ADMIN_JWT_EXPIRE_MINUTES = int(os.getenv("ADMIN_JWT_EXPIRE_MINUTES", "120"))


def verify_admin_password(password: str) -> bool:
    """验证管理员密码（bcrypt 加密）"""
    try:
        is_valid = bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())
        auth_logger.debug(f"管理员密码验证：{'成功' if is_valid else '失败'}")
        return is_valid
    except Exception as e:
        auth_logger.error(f"管理员密码验证异常：{e}")
        return False


def create_admin_token() -> str:
    """创建管理员访问令牌"""
    expire = datetime.utcnow() + timedelta(minutes=ADMIN_JWT_EXPIRE_MINUTES)
    to_encode = {
        "sub": "admin",
        "role": "admin",
        "exp": expire
    }
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    auth_logger.info(f"管理员令牌创建成功，过期时间：{expire}")
    return token


def decode_admin_token(token: str) -> Optional[str]:
    """解码管理员令牌，返回 role"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = payload.get("role")
        if role == "admin":
            auth_logger.debug("管理员令牌验证成功")
            return role
        auth_logger.warning("令牌角色不是管理员")
        return None
    except JWTError as e:
        auth_logger.warning(f"管理员令牌解码失败：{e}")
        return None
    except Exception as e:
        auth_logger.error(f"管理员令牌解析异常：{e}")
        return None


def get_admin_token_expire_seconds() -> int:
    """获取 Token 有效期（秒）"""
    return ADMIN_JWT_EXPIRE_MINUTES * 60
