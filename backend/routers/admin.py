"""管理员后台路由"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from models.admin import (
    AdminLogin, AdminTokenResponse,
    UserResponse, UserDetailResponse, UserListResponse,
    OperationLogResponse, OperationLogListResponse,
    DisableUserRequest
)
from services.admin_auth import verify_admin_password, create_admin_token, decode_admin_token, get_admin_token_expire_seconds
from services.admin_operation_log import log_operation, get_operation_logs
from services.user_store import get_all_users, get_user_by_id_with_status, set_user_disabled
from services.question_record_store import get_user_records
from utils.logger import api_logger

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer(auto_error=False)


# ========== 认证依赖 ==========

def get_current_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """获取当前管理员（依赖注入）"""
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录")

    token = credentials.credentials
    role = decode_admin_token(token)
    if not role:
        raise HTTPException(status_code=401, detail="登录已过期")

    return "admin"


async def get_request_ip(request: Request) -> str:
    """获取请求 IP"""
    return request.client.host if request.client else "unknown"


# ========== 公开接口（无需认证）==========

@router.post("/login", response_model=AdminTokenResponse)
async def admin_login(request: AdminLogin, req: Request):
    """管理员登录"""
    ip = req.client.host if req.client else "unknown"

    # 验证密码
    if not verify_admin_password(request.password):
        api_logger.warning(f"管理员登录失败 - 密码错误，IP: {ip}")
        log_operation(operator="unknown", action="login_failed", target_type="admin", ip=ip, details="密码错误")
        raise HTTPException(status_code=401, detail="密码错误")

    # 创建 token
    token = create_admin_token()
    expires_in = get_admin_token_expire_seconds()

    api_logger.info(f"管理员登录成功，IP: {ip}")
    log_operation(operator="admin", action="login_success", target_type="admin", ip=ip)

    return AdminTokenResponse(
        access_token=token,
        expires_in=expires_in
    )


# ========== 需要认证的接口 ==========

@router.get("/me")
async def get_admin_me(admin: str = Depends(get_current_admin)):
    """获取当前管理员状态"""
    return {"role": "admin", "authenticated": True}


@router.get("/users", response_model=UserListResponse)
async def get_all_users_list(
    page: int = 1,
    page_size: int = 20,
    admin: str = Depends(get_current_admin),
):
    """获取所有用户列表（分页）"""
    users, total, has_more = get_all_users(page, page_size)

    return UserListResponse(
        data=users,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int,
    req: Request,
    admin: str = Depends(get_current_admin),
):
    """获取用户详情（含统计信息）"""
    ip = req.client.host if req.client else "unknown"

    user = get_user_by_id_with_status(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户的题目记录统计
    total_records = 0
    last_activity = None
    try:
        records, _, _ = get_user_records(user_id, None, 1)  # 只查一条判断是否有
        total_records = len(records)
        # 获取最近活动时间 - 转换为字符串
        if records:
            last_activity = str(records[0].created_at)
    except Exception as e:
        api_logger.error(f"获取用户记录失败：{e}")

    log_operation(
        operator="admin",
        action="view_user",
        target_type="user",
        target_id=user_id,
        ip=ip
    )

    return UserDetailResponse(
        id=user["id"],
        email=user["email"],
        created_at=str(user["created_at"]),
        is_disabled=user["is_disabled"],
        total_records=total_records,
        last_activity=last_activity
    )


@router.post("/users/{user_id}/disable")
async def disable_user(
    user_id: int,
    request: DisableUserRequest,
    req: Request,
    admin: str = Depends(get_current_admin),
):
    """禁用/启用用户"""
    ip = req.client.host if req.client else "unknown"

    # 检查用户是否存在
    user = get_user_by_id_with_status(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新状态
    success = set_user_disabled(user_id, request.is_disabled)
    if not success:
        raise HTTPException(status_code=500, detail="更新用户状态失败")

    action = "disable_user" if request.is_disabled else "enable_user"
    api_logger.info(f"用户状态更新成功：user_id={user_id}, is_disabled={request.is_disabled}")

    log_operation(
        operator="admin",
        action=action,
        target_type="user",
        target_id=user_id,
        ip=ip,
        details=f"{'禁用' if request.is_disabled else '启用'}用户 {user['email']}"
    )

    return {"message": "操作成功"}


@router.get("/users/{user_id}/records")
async def get_user_question_records(
    user_id: int,
    req: Request,
    cursor: Optional[int] = None,
    limit: int = 20,
    admin: str = Depends(get_current_admin),
):
    """获取用户的题目生成记录"""
    ip = req.client.host if req.client else "unknown"

    try:
        records, next_cursor, has_more = get_user_records(user_id, cursor, limit)

        log_operation(
            operator="admin",
            action="view_user_records",
            target_type="user",
            target_id=user_id,
            ip=ip
        )

        return {
            "data": records,
            "next_cursor": next_cursor,
            "has_more": has_more
        }
    except Exception as e:
        api_logger.error(f"获取用户记录失败：{e}")
        raise HTTPException(status_code=500, detail="获取用户记录失败")


@router.get("/operation-logs", response_model=OperationLogListResponse)
async def get_operation_logs_list(
    page: int = 1,
    page_size: int = 20,
    admin: str = Depends(get_current_admin)
):
    """获取操作日志列表"""
    logs, total, has_more = get_operation_logs(page, page_size)

    return OperationLogListResponse(
        data=logs,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )
