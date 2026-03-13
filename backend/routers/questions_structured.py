"""
结构化题目生成接口
返回符合 JSON Schema 的结构化数据
"""
import traceback
import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.qwen_client import generate_questions_async
from services.question_record_store import create_record, QuestionRecordCreate, get_record_by_short_id
from routers.auth import get_current_user_email
from services.user_store import get_user as get_user_by_email
from utils.logger import api_logger, qwen_logger
from utils.validators import validate_prompt
from utils.json_validator import validate_question_json, extract_question_text
from models.structured_question import (
    QuestionBank,
    MetaData,
    calculate_rows_to_answer
)

router = APIRouter(prefix="/api/questions", tags=["questions"])


class StructuredGenerateRequest(BaseModel):
    """结构化题目生成请求"""
    prompt: str


class StructuredQuestionResponse(BaseModel):
    """单个结构化题目响应（含后端填充字段）"""
    type: str
    stem: str
    knowledge_points: List[str]
    options: Optional[List[str]]
    passage: Optional[str]
    sub_questions: Optional[List["StructuredQuestionResponse"]]
    rows_to_answer: int


StructuredQuestionResponse.update_forward_refs()


class StructuredGenerateResponse(BaseModel):
    """结构化题目生成响应"""
    meta: MetaData
    questions: List[StructuredQuestionResponse]
    record_id: Optional[int] = None
    short_id: Optional[str] = None
    created_at: Optional[datetime] = None


def convert_to_structured_response(question: "Question") -> StructuredQuestionResponse:
    """
    递归转换题目为 StructuredQuestionResponse
    """
    from models.structured_question import Question as StructuredQuestion
    sub_questions = None
    if question.sub_questions:
        sub_questions = [
            convert_to_structured_response(sq)
            for sq in question.sub_questions
        ]

    return StructuredQuestionResponse(
        type=question.type,
        stem=question.stem,
        knowledge_points=question.knowledge_points,
        options=question.options,
        passage=question.passage,
        sub_questions=sub_questions,
        rows_to_answer=calculate_rows_to_answer(question)
    )


@router.post("/structured", response_model=StructuredGenerateResponse)
async def generate_structured(
    request: StructuredGenerateRequest,
    email: str = Depends(get_current_user_email),
):
    """
    根据提示词生成结构化题目并保存历史记录

    返回结构化 JSON 数据，包含：
    - meta: 元数据（subject, grade, title）
    - questions: 题目列表（含 rows_to_answer 等后端填充字段）
    """
    api_logger.info(f"结构化题目生成请求，email: {email}, prompt: {(request.prompt or '')[:50]}...")

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
        api_logger.info(f"开始调用结构化题目生成服务，email: {email}")

        # 获取用户 ID
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 调用 AI 生成题目
        # AI 现在应该返回 JSON 格式
        title, content = await generate_questions_async(prompt, user_id=user.id)

        if not content:
            api_logger.error(f"AI 返回内容为空，email: {email}")
            raise HTTPException(status_code=502, detail="AI 返回内容为空")

        # 校验 JSON 格式
        is_valid, data, errors = validate_question_json(content)

        if not is_valid:
            api_logger.error(f"JSON 校验失败，email: {email}, errors: {errors}")
            # 尝试解析 JSON 并输出更详细的错误信息
            try:
                parsed = json.loads(content)
                questions = parsed.get("questions", [])
                for idx, q in enumerate(questions):
                    if q.get("type") == "SINGLE_CHOICE" and q.get("options"):
                        for opt_idx, opt in enumerate(q.get("options", [])[:3]):  # 只检查前3个选项
                            if "\\\\" in opt:  # 检测双反斜杠
                                api_logger.error(f"选项第 {idx} 题第 {opt_idx} 选项存在双反斜杠: {opt[:100]}")
            except:
                pass
            raise HTTPException(
                status_code=502,
                detail=f"JSON 校验失败: {'；'.join(errors)}"
            )

        # 解析题库数据
        try:
            question_bank = QuestionBank(**data)
        except Exception as e:
            api_logger.error(f"题库数据解析失败，email: {email}, error: {e}")
            raise HTTPException(status_code=502, detail=f"数据解析失败: {str(e)}")

        api_logger.info(f"题目生成成功，email: {email}, 题目数量: {len(question_bank.questions)}")

        # 从解析后的数据中重新提取标题（确保使用正确的 title）
        actual_title = question_bank.meta.title if question_bank.meta.title else title
        api_logger.info(f"[标题提取] 从 meta.title 提取: {actual_title}")

        # 转换为响应格式（填充 rows_to_answer 等字段）
        structured_questions = [
            convert_to_structured_response(q)
            for q in question_bank.questions
        ]

        # 保存历史记录（原始 JSON 字符串）
        try:
            record = QuestionRecordCreate(
                title=actual_title,  # 使用正确的标题
                prompt_type="text",
                prompt_content=prompt,
                ai_response=content,  # 保存原始 JSON
                image_path=None,
            )
            record_id, short_id = create_record(user.id, record)
            api_logger.info(f"历史记录保存成功：id={record_id}, short_id={short_id}, title={actual_title}")
        except Exception as e:
            api_logger.error(f"历史记录保存失败：{e}")
            record_id = None
            short_id = None

        return StructuredGenerateResponse(
            meta=MetaData(
                subject=question_bank.meta.subject,
                grade=question_bank.meta.grade,
                title=question_bank.meta.title
            ),
            questions=structured_questions,
            record_id=record_id,
            short_id=short_id,
            created_at=datetime.utcnow()
        )

    except ValueError as e:
        api_logger.error(f"题目生成失败 - 配置错误，email: {email}, error: {e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        api_logger.error(f"题目生成失败 - API 错误，email: {email}, error: {e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=502, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"题目生成失败 - 未知错误，email: {email}, error: {e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
