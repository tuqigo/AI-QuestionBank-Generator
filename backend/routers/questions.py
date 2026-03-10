from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.qwen_client import generate_questions_async
from services.question_record_store import create_record, QuestionRecordCreate
from routers.auth import get_current_user_email
from services.user_store import get_user as get_user_by_email
from utils.logger import api_logger, qwen_logger

router = APIRouter(prefix="/api/questions", tags=["questions"])


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    title: str
    markdown: str


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    email: str = Depends(get_current_user_email),
):
    """根据提示词生成题目并保存历史记录"""
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
        # 调用 AI 生成题目，返回 (标题，内容) - 使用异步版本
        title, markdown = await generate_questions_async(prompt)

        # 获取用户 ID
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 保存历史记录（异步，不阻塞主流程）
        try:
            record = QuestionRecordCreate(
                title=title,
                prompt_type="text",
                prompt_content=prompt,
                ai_response=markdown,
                image_path=None,
            )
            record_id = create_record(user.id, record)
            api_logger.info(f"历史记录保存成功：id={record_id}, user_id={user.id}")
        except Exception as e:
            api_logger.error(f"历史记录保存失败：{e}")
            # 保存失败不阻塞主流程

        api_logger.info(f"题目生成成功，email: {email}, 标题：{title}, 内容长度：{len(markdown) if markdown else 0}")
        return GenerateResponse(title=title, markdown=markdown)
    except ValueError as e:
        api_logger.error(f"题目生成失败 - 配置错误，email: {email}, error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        api_logger.error(f"题目生成失败 - API 错误，email: {email}, error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
