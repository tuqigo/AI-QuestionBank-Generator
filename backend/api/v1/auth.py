from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Tuple
import re

from config import OTP_EXPIRE_MINUTES, OTP_RATE_LIMIT_WINDOW, OTP_RATE_LIMIT_MAX
from models.user import (
    UserCreate, UserLogin, TokenResponse,
    EmailOtpRequest, ResetPasswordRequest
)
from services.auth import verify_password, create_access_token, decode_token, get_password_hash
from services.user.user_store import get_user, create_user, update_password
from services.email_sender import send_otp_email
from models.otp import generate_code, store_otp, verify_otp, check_rate_limit
from utils.logger import auth_logger, api_logger

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


def _validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _validate_password(password: str) -> Tuple[bool, str]:
    """验证密码强度，返回 (是否有效，错误信息)"""
    if len(password) < 8:
        return False, "密码至少 8 个字符"
    if len(password) > 32:
        return False, "密码不能超过 32 个字符"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, ""


@router.post("/send-otp")
async def send_otp(request: EmailOtpRequest, req: Request):
    """发送邮箱验证码（注册或找回密码）"""
    email = (request.email or "").strip().lower()
    purpose = request.purpose or "register"

    # 验证用途
    if purpose not in ["register", "reset_password"]:
        raise HTTPException(status_code=400, detail="无效的验证码用途")

    # 邮箱格式验证
    if not _validate_email(email):
        api_logger.warning(f"发送验证码失败 - 邮箱格式无效：{email}")
        raise HTTPException(status_code=400, detail="邮箱格式无效")

    # 速率限制检查
    ip = req.client.host if req.client else "unknown"
    if not check_rate_limit(email, purpose, ip, OTP_RATE_LIMIT_WINDOW, OTP_RATE_LIMIT_MAX):
        api_logger.warning(f"发送验证码失败 - 速率限制，email: {email}, purpose: {purpose}")
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

    # 注册时检查邮箱是否已存在
    if purpose == "register":
        existing_user = get_user(email)
        if existing_user:
            api_logger.warning(f"发送验证码失败 - 邮箱已注册：{email}")
            raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 找回密码时检查邮箱是否存在
    if purpose == "reset_password":
        existing_user = get_user(email)
        if not existing_user:
            api_logger.warning(f"发送验证码失败 - 邮箱未注册：{email}")
            raise HTTPException(status_code=400, detail="该邮箱未注册")

    # 生成并存储验证码
    code = generate_code()
    if not store_otp(email, code, purpose, OTP_EXPIRE_MINUTES):
        api_logger.error(f"发送验证码失败 - 存储验证码失败，email: {email}")
        raise HTTPException(status_code=500, detail="系统错误")

    # 发送邮件
    subject_prefix = f"{'注册' if purpose == 'register' else '找回密码'}验证码"
    if not send_otp_email(email, code, OTP_EXPIRE_MINUTES, subject_prefix):
        api_logger.error(f"发送验证码失败 - 邮件发送失败，email: {email}")
        raise HTTPException(status_code=500, detail="邮件发送失败")

    api_logger.info(f"验证码发送成功，email: {email}, purpose: {purpose}")
    return {"message": "验证码已发送", "email": email}


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate):
    """邮箱 + 密码注册（需要验证码）"""
    email = (data.email or "").strip().lower()
    password = data.password or ""
    code = (data.code or "").strip()

    # 验证邮箱
    if not _validate_email(email):
        api_logger.warning(f"注册失败 - 邮箱格式无效：{email}")
        raise HTTPException(status_code=400, detail="邮箱格式无效")

    # 验证密码
    valid, msg = _validate_password(password)
    if not valid:
        api_logger.warning(f"注册失败 - 密码无效：{msg}")
        raise HTTPException(status_code=400, detail=msg)

    # 验证验证码
    if not code or len(code) != 6 or not code.isdigit():
        api_logger.warning(f"注册失败 - 验证码格式无效")
        raise HTTPException(status_code=400, detail="验证码为 6 位数字")

    if not verify_otp(email, code, "register"):
        api_logger.warning(f"注册失败 - 验证码错误，email: {email}")
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # 创建用户
    try:
        create_user(email, password)
        token = create_access_token({"sub": email})
        api_logger.info(f"注册成功，email: {email}")
        return TokenResponse(access_token=token)
    except ValueError as e:
        api_logger.warning(f"注册失败 - 用户已存在：{email}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """邮箱 + 密码登录"""
    email = (data.email or "").strip().lower()
    password = data.password or ""

    # 验证邮箱
    if not _validate_email(email):
        api_logger.warning(f"登录失败 - 邮箱格式无效：{email}")
        raise HTTPException(status_code=400, detail="邮箱格式无效")

    user = get_user(email)
    if not user:
        api_logger.warning(f"登录失败 - 用户不存在：{email}")
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    # 验证密码（空密码表示该用户是通过其他方式创建的）
    if not user.hashed_password:
        api_logger.warning(f"登录失败 - 用户未设置密码：{email}")
        raise HTTPException(status_code=401, detail="请先设置密码")

    if not verify_password(password, user.hashed_password):
        api_logger.warning(f"登录失败 - 密码错误，email: {email}")
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    token = create_access_token({"sub": email})
    api_logger.info(f"登录成功，email: {email}")
    return TokenResponse(access_token=token)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """邮箱验证码重置密码"""
    email = (request.email or "").strip().lower()
    code = (request.code or "").strip()
    new_password = request.new_password or ""

    # 验证邮箱
    if not _validate_email(email):
        api_logger.warning(f"重置密码失败 - 邮箱格式无效：{email}")
        raise HTTPException(status_code=400, detail="邮箱格式无效")

    # 验证密码
    valid, msg = _validate_password(new_password)
    if not valid:
        api_logger.warning(f"重置密码失败 - 密码无效：{msg}")
        raise HTTPException(status_code=400, detail=msg)

    # 验证验证码
    if not code or len(code) != 6 or not code.isdigit():
        api_logger.warning(f"重置密码失败 - 验证码格式无效")
        raise HTTPException(status_code=400, detail="验证码为 6 位数字")

    if not verify_otp(email, code, "reset_password"):
        api_logger.warning(f"重置密码失败 - 验证码错误，email: {email}")
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # 更新密码
    try:
        update_password(email, new_password)
        api_logger.info(f"重置密码成功，email: {email}")
        return {"message": "密码重置成功"}
    except ValueError as e:
        api_logger.warning(f"重置密码失败 - 用户不存在：{email}")
        raise HTTPException(status_code=400, detail=str(e))


def get_current_user_email(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """获取当前登录用户邮箱 - 用于 Depends 注入"""
    if not credentials:
        api_logger.warning("未提供认证凭据")
        raise HTTPException(status_code=401, detail="未登录")

    email = decode_token(credentials.credentials)
    if not email:
        api_logger.warning("令牌无效或已过期")
        raise HTTPException(status_code=401, detail="登录已过期")

    user = get_user(email)
    if not user:
        api_logger.warning(f"用户不存在：{email}")
        raise HTTPException(status_code=401, detail="用户不存在")

    return email


@router.get("/me")
async def me(email: str = Depends(get_current_user_email)):
    """获取当前用户信息"""
    api_logger.debug(f"获取当前用户信息：{email}")
    user = get_user(email)
    return {"email": email, "grade": user.grade if user else None}


@router.post("/logout")
async def logout():
    """登出 - 客户端清除 token 即可"""
    api_logger.debug("登出请求")
    return {"message": "登出成功"}
