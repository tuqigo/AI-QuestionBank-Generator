from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.qwen_client import generate_questions
from routers.auth import get_current_user_email
from utils.logger import api_logger, qwen_logger

router = APIRouter(prefix="/api/questions", tags=["questions"])


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    markdown: str


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    email: str = Depends(get_current_user_email),
):
    api_logger.info(f"题目生成请求，email: {email}, prompt: {(request.prompt or '')[:50]}...")

    prompt = (request.prompt or "").strip()
    if not prompt:
        api_logger.warning(f"题目生成失败 - 提示词为空，email: {email}")
        raise HTTPException(status_code=400, detail="提示词不能为空")
    if len(prompt) > 2000:
        api_logger.warning(f"题目生成失败 - 提示词过长，email: {email}")
        raise HTTPException(status_code=400, detail="提示词过长")

    try:
        api_logger.info(f"开始调用题目生成服务，email: {email}")
        markdown = generate_questions(prompt)
        api_logger.info(f"题目生成成功，email: {email}, 内容长度：{len(markdown) if markdown else 0}")
        return GenerateResponse(markdown=markdown)
    except ValueError as e:
        api_logger.error(f"题目生成失败 - 配置错误，email: {email}, error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        api_logger.error(f"题目生成失败 - API 错误，email: {email}, error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
