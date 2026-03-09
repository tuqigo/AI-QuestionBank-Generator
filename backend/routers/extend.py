"""图片上传生成扩展题"""

import base64
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form

from routers.auth import get_current_user_email
from services.qwen_vision import extend_questions_from_image
from services.user_store import get_user
from services.question_record_store import create_record, QuestionRecordCreate
from utils.logger import api_logger

router = APIRouter(prefix="/api/questions", tags=["questions"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def get_media_type(content_type: str) -> str:
    if "jpeg" in content_type or "jpg" in content_type:
        return "jpeg"
    if "png" in content_type:
        return "png"
    if "webp" in content_type:
        return "webp"
    if "gif" in content_type:
        return "gif"
    return "jpeg"


@router.post("/extend-from-image")
async def extend_from_image(
    file: UploadFile = File(...),
    hint: str = Form(""),
    email: str = Depends(get_current_user_email),
):
    """上传图片识别并生成扩展题，同时保存历史记录"""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 jpeg、png、webp、gif 格式图片")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")
    try:
        image_base64 = base64.b64encode(content).decode("utf-8")
        media_type = get_media_type(file.content_type or "")
        title, markdown = extend_questions_from_image(image_base64, media_type, hint.strip())

        # 保存历史记录
        user = get_user(email)
        if user:
            try:
                record = QuestionRecordCreate(
                    title=title,
                    prompt_type="image",
                    prompt_content=hint.strip() or "图片识别扩展",
                    ai_response=markdown,
                    image_path=None,
                )
                record_id = create_record(user.id, record)
                api_logger.info(f"图片扩展历史记录保存成功：id={record_id}, user_id={user.id}")
            except Exception as e:
                api_logger.error(f"图片扩展历史记录保存失败：{e}")

        return {"title": title, "markdown": markdown}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
