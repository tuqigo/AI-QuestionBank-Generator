from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from typing import Optional

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from utils.logger import auth_logger


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    # bcrypt 限制密码最大 72 字节，需要手动截断
    try:
        result = bcrypt.checkpw(plain[:72].encode('utf-8'), hashed.encode('utf-8'))
        auth_logger.debug(f"密码验证：{'成功' if result else '失败'}")
        return result
    except Exception as e:
        auth_logger.error(f"密码验证异常：{e}")
        return False


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # bcrypt 限制密码最大 72 字节，需要手动截断
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password[:72].encode('utf-8'), salt)
    result = hashed.decode('utf-8')
    auth_logger.debug(f"密码哈希完成")
    return result


def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    auth_logger.debug(f"访问令牌创建成功，过期时间：{expire}")
    return token


def decode_token(token: str) -> Optional[str]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        auth_logger.debug(f"令牌解码成功，用户：{username}")
        return username
    except JWTError as e:
        auth_logger.warning(f"令牌解码失败：{e}")
        return None
    except Exception as e:
        auth_logger.error(f"令牌解析异常：{e}")
        return None
