import traceback
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.ai.qwen_client import generate_questions_async
from services.question.question_record_store import create_record, QuestionRecordCreate, get_record_by_short_id
from api.v1.auth import get_current_user_email
from services.user.user_store import get_user as get_user_by_email
from utils.logger import api_logger, qwen_logger
from utils.validators import validate_prompt

router = APIRouter(prefix="/api/questions", tags=["questions"])


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    title: str
    markdown: str
    record_id: Optional[int] = None
    short_id: Optional[str] = None


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

    # 使用统一的校验函数
    error_msg = validate_prompt(prompt)
    if error_msg:
        api_logger.warning(f"题目生成失败 - 提示词校验失败：{error_msg}, email: {email}")
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        api_logger.info(f"开始调用题目生成服务，email: {email}")
        # 获取用户 ID
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 调用 AI 生成题目，返回 (标题，内容) - 使用异步版本
        title, markdown = await generate_questions_async(prompt, user_id=user.id)

        # 保存历史记录（异步，不阻塞主流程）
        try:
            record = QuestionRecordCreate(
                title=title,
                prompt_type="text",
                prompt_content=prompt,
                ai_response=markdown,
                image_path=None,
            )
            record_id, short_id = create_record(user.id, record)
            api_logger.info(f"历史记录保存成功：id={record_id}, short_id={short_id}, user_id={user.id}")
        except Exception as e:
            api_logger.error(f"历史记录保存失败：{e}")
            record_id = None
            short_id = None
            # 保存失败不阻塞主流程

        api_logger.info(f"题目生成成功，email: {email}, 标题：{title}, 内容长度：{len(markdown) if markdown else 0}")
        return GenerateResponse(title=title, markdown=markdown, record_id=record_id, short_id=short_id)
    except ValueError as e:
        api_logger.error(f"题目生成失败 - 配置错误，email: {email}, error: {e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        api_logger.error(f"题目生成失败 - API 错误，email: {email}, error: {e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        api_logger.error(f"题目生成失败 - 未知错误，email: {email}, error: {e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
