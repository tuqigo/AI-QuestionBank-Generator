from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel
from typing import Optional

from routers.auth import get_current_user_email
from services.question_record_store import (
    create_record,
    get_record_by_id,
    get_record_by_short_id,
    get_record_by_share_token,
    get_user_records,
    soft_delete_record,
    generate_share_token,
    get_user_record_count,
    delete_oldest_record,
)
from services.user_store import get_user as get_user_by_email
from models.question_record import (
    QuestionRecordCreate,
    QuestionRecordResponse,
    QuestionRecordListResponse,
    ShareTokenResponse,
)
from utils.logger import api_logger

router = APIRouter(prefix="/api/history", tags=["history"])

# 配置：每用户最大记录数
MAX_RECORDS_PER_USER = 1000


class ShareUrlResponse(BaseModel):
    """分享链接响应"""
    share_url: str


class CreateHistoryRequest(BaseModel):
    """创建历史记录请求（内部使用）"""
    title: str
    prompt_type: str
    prompt_content: str
    ai_response: str
    image_path: Optional[str] = None


@router.post("", response_model=dict)
async def create_history(
    request: CreateHistoryRequest,
    email: str = Depends(get_current_user_email),
):
    """创建历史记录（内部调用，保存 AI 生成结果）"""
    # 获取用户 ID
    user = get_user_by_email(email)

    if not user:
        api_logger.warning(f"创建历史记录失败 - 用户不存在：{email}")
        raise HTTPException(status_code=404, detail="用户不存在")

    user_id = user.id

    # 检查记录数量限制（FIFO）
    current_count = get_user_record_count(user_id)
    if current_count >= MAX_RECORDS_PER_USER:
        # 删除最早的记录
        delete_oldest_record(user_id)
        api_logger.info(f"达到记录上限，已删除最早记录：user_id={user_id}")

    # 创建记录
    record = QuestionRecordCreate(
        title=request.title,
        prompt_type=request.prompt_type,
        prompt_content=request.prompt_content,
        ai_response=request.ai_response,
        image_path=request.image_path,
    )

    try:
        record_id, short_id = create_record(user_id, record)
        api_logger.info(f"历史记录创建成功：id={record_id}, short_id={short_id}, user_id={user_id}")
        return {"id": record_id, "short_id": short_id, "message": "保存成功"}
    except Exception as e:
        api_logger.error(f"创建历史记录失败：{e}")
        # 保存失败不阻塞主流程，返回成功但记录日志
        return {"id": None, "message": "保存失败，已记录日志"}


@router.get("", response_model=QuestionRecordListResponse)
async def get_history_list(
    cursor: Optional[int] = Query(None, description="上一页最后一条记录的 ID"),
    size: Optional[int] = Query(20, ge=1, le=100, description="每页数量"),
    email: str = Depends(get_current_user_email),
):
    """获取用户历史记录列表（游标分页）"""
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_id = user.id

    try:
        records, next_cursor, has_more = get_user_records(user_id, cursor, size)
        return QuestionRecordListResponse(
            data=records,
            next_cursor=next_cursor,
            has_more=has_more,
        )
    except Exception as e:
        api_logger.error(f"获取历史记录列表失败：{e}")
        raise HTTPException(status_code=500, detail="获取历史记录失败")


@router.get("/{record_id}", response_model=QuestionRecordResponse)
async def get_history_detail(
    record_id: str,
    email: str = Depends(get_current_user_email),
):
    """获取单条历史记录详情（支持 short_id）"""
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_id = user.id

    # 尝试用 short_id 查询
    record = get_record_by_short_id(record_id, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    return record


@router.delete("/{record_id}")
async def delete_history(
    record_id: str,
    email: str = Depends(get_current_user_email),
):
    """删除历史记录（软删除）"""
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_id = user.id

    # 先通过 short_id 获取记录，得到真正的 id
    record = get_record_by_short_id(record_id, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    success = soft_delete_record(record.id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")

    return {"message": "删除成功"}


@router.post("/{record_id}/share", response_model=ShareUrlResponse)
async def create_share_url(
    record_id: str,
    request: Request,
    email: str = Depends(get_current_user_email),
):
    """生成分享链接"""
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user_id = user.id

    # 先通过 short_id 获取记录，得到真正的 id
    record = get_record_by_short_id(record_id, user_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 生成或获取 share token
    token = generate_share_token(record.id, user_id)
    if not token:
        raise HTTPException(status_code=500, detail="生成分享链接失败")

    # 返回分享链接（前端会拼接完整 URL）- 使用 short_id
    return ShareUrlResponse(share_url=f"/share/h/{record.short_id}?token={token}")


# ========== 分享接口（独立路由，避免与 /{record_id} 冲突）==========
# 使用单独的路由器，前缀为 /api/share/history
share_router = APIRouter(prefix="/api/share/history", tags=["share"])


@share_router.get("/{record_id}", response_model=QuestionRecordResponse)
async def get_share_record(record_id: str, token: Optional[str] = Query(None)):
    """通过分享链接获取记录（无需登录）"""
    if not token:
        raise HTTPException(status_code=404, detail="分享链接无效：缺少 token 参数")

    record = get_record_by_share_token(token)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在或分享链接无效")

    return record
