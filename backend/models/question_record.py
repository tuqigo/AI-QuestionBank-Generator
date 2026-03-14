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
    """题目记录响应模型（详情）"""
    id: int
    short_id: str  # 对外暴露的短 ID
    title: str
    prompt_type: str
    prompt_content: str
    image_path: Optional[str]
    ai_response: str
    is_deleted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionRecordListItem(BaseModel):
    """题目记录列表项（精简版）"""
    id: int
    short_id: str
    title: str
    prompt_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionRecordListResponse(BaseModel):
    """题目记录列表响应（游标分页）"""
    data: List[QuestionRecordListItem]
    next_cursor: Optional[int] = None
    has_more: bool = False


class ShareTokenResponse(BaseModel):
    """分享 Token 响应"""
    share_token: str
    share_url: str
