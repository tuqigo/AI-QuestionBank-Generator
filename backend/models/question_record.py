from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionRecordCreate(BaseModel):
    """创建题目记录的请求模型"""
    title: str
    prompt_type: str  # 'text' or 'image'
    prompt_content: str
    ai_response: str
    image_path: Optional[str] = None


class QuestionRecordUpdate(BaseModel):
    """更新题目记录的请求模型"""
    title: Optional[str] = None
    prompt_content: Optional[str] = None
    ai_response: Optional[str] = None


class QuestionRecordResponse(BaseModel):
    """题目记录响应模型"""
    id: int
    title: str
    prompt_type: str
    prompt_content: str
    image_path: Optional[str]
    ai_response: str
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionRecordListResponse(BaseModel):
    """题目记录列表响应（游标分页）"""
    data: List[QuestionRecordResponse]
    next_cursor: Optional[int] = None
    has_more: bool = False


class ShareTokenResponse(BaseModel):
    """分享 Token 响应"""
    share_token: str
    share_url: str
