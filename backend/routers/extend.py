"""图片上传生成扩展题"""

import base64
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form

from routers.auth import get_current_user_email
from services.qwen_vision import extend_questions_from_image

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
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 jpeg、png、webp、gif 格式图片")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")
    try:
        image_base64 = base64.b64encode(content).decode("utf-8")
        media_type = get_media_type(file.content_type or "")
        markdown = extend_questions_from_image(image_base64, media_type, hint.strip())
        return {"markdown": markdown}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
