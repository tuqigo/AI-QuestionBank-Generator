"""JWT 认证中间件和装饰器"""

from functools import wraps
from typing import Optional, Callable
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth import decode_token
from utils.logger import auth_logger

security = HTTPBearer(auto_error=False)


def get_current_username(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """获取当前登录用户名 - 用于 Depends 注入"""
    if not credentials:
        auth_logger.warning("未提供认证凭据")
        raise HTTPException(status_code=401, detail="未登录")

    username = decode_token(credentials.credentials)
    if not username:
        auth_logger.warning("令牌无效或已过期")
        raise HTTPException(status_code=401, detail="登录已过期")

    return username


def Jwt(required: bool = True):
    """
    JWT 认证装饰器

    用法:
        @router.get("/protected")
        @Jwt()  # 需要认证
        async def protected_route(username: str = Depends(get_current_username)):
            ...

        @router.get("/optional")
        @Jwt(required=False)  # 可选认证
        async def optional_route(username: Optional[str] = Depends(get_current_username_optional)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 实际认证由 Depends(get_current_username) 处理
            # 此装饰器主要用于标记接口需要认证
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def get_current_username_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """获取当前登录用户名（可选）- 未提供凭证时返回 None"""
    if not credentials:
        return None

    username = decode_token(credentials.credentials)
    if not username:
        return None

    return username
