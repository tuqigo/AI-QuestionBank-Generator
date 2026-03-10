"""管理员相关 Pydantic 模型"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AdminLogin(BaseModel):
    """管理员登录请求"""
    password: str


class AdminTokenResponse(BaseModel):
    """管理员登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    email: str
    created_at: str
    is_disabled: bool = False


class UserDetailResponse(UserResponse):
    """用户详情响应（含统计）"""
    total_records: int = 0
    last_activity: Optional[str] = None


class UserListResponse(BaseModel):
    """用户列表响应"""
    data: List[UserResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class OperationLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    operator: str
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    ip: Optional[str]
    created_at: str


class OperationLogListResponse(BaseModel):
    """操作日志列表响应"""
    data: List[OperationLogResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class DisableUserRequest(BaseModel):
    """禁用/启用用户请求"""
    is_disabled: bool  # true=禁用，false=启用
