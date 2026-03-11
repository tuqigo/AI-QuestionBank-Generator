"""AI 生成记录模型"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AiGenerationRecordCreate(BaseModel):
    """创建 AI 生成记录的请求模型"""
    user_id: int
    prompt: str
    prompt_type: str  # 'text' or 'vision'
    success: bool
    duration: float  # 耗时（秒）
    error_message: Optional[str] = None


class AiGenerationRecordResponse(BaseModel):
    """AI 生成记录响应模型"""
    id: int
    user_id: int
    user_email: str  # 关联用户的 email
    prompt: str
    prompt_type: str  # 'text' or 'vision'
    success: bool
    duration: float
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AiGenerationRecordListResponse(BaseModel):
    """AI 生成记录列表响应（分页）"""
    data: List[AiGenerationRecordResponse]
    total: int
    page: int
    page_size: int
    has_more: bool = False


class AiGenerationRecordFilter(BaseModel):
    """筛选条件"""
    user_id: Optional[int] = None
    success: Optional[bool] = None
    prompt_type: Optional[str] = None
    date_from: Optional[str] = None  # YYYY-MM-DD
    date_to: Optional[str] = None    # YYYY-MM-DD
