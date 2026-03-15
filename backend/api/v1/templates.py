"""
题目模板 API 接口
"""
import traceback
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from models.question_template import (
    QuestionTemplateListItem,
    QuestionTemplateListResponse,
    TemplateGenerateRequest,
    TemplateGenerateResponse,
)
from services.template.template_store import (
    get_template_by_id,
    get_template_list_items,
)
from services.template.generators import get_generator
from api.v1.auth import get_current_user_email
from services.user.user_store import get_user as get_user_by_email
from utils.logger import api_logger

router = APIRouter(prefix="/api/templates", tags=["templates"])


class TemplateListItem(BaseModel):
    """模板列表项"""
    id: int
    name: str
    subject: str
    grade: str
    example: Optional[str]


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    templates: list[TemplateListItem]


class TemplateGenerateResponse(BaseModel):
    """模板生成题目响应"""
    meta: dict = Field(..., description="元数据")
    questions: list[dict] = Field(..., description="题目列表")


@router.get("/list", response_model=TemplateListResponse)
async def get_templates():
    """
    获取所有启用的模板列表

    返回精简版模板信息，用于前端下拉选择
    """
    api_logger.info("获取模板列表请求")

    try:
        templates = get_template_list_items()
        return TemplateListResponse(
            templates=[
                TemplateListItem(
                    id=t.id,
                    name=t.name,
                    subject=t.subject,
                    grade=t.grade,
                    example=t.example,
                )
                for t in templates
            ]
        )
    except Exception as e:
        api_logger.error(f"获取模板列表失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=TemplateGenerateResponse)
async def generate_from_template(
    request: TemplateGenerateRequest,
    email: str = Depends(get_current_user_email),
):
    """
    根据模板 ID 生成题目

    请求参数：
    - template_id: 模板 ID
    - quantity: 题目数量（默认 15，范围 5-50）

    返回：
    - meta: 元数据（subject, grade, title）
    - questions: 题目列表（结构化数据）

    注意：模板生成的题目不保存历史记录，是一次性使用
    """
    api_logger.info(f"模板题目生成请求，email: {email}, template_id: {request.template_id}, quantity: {request.quantity}")

    # 获取模板
    template = get_template_by_id(request.template_id)
    if not template:
        api_logger.warning(f"模板不存在：template_id={request.template_id}")
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查模板是否启用
    if not template.is_active:
        api_logger.warning(f"模板未启用：template_id={request.template_id}")
        raise HTTPException(status_code=400, detail="模板未启用")

    # 获取用户（校验登录状态）
    user = get_user_by_email(email)
    if not user:
        api_logger.warning(f"用户不存在：email={email}")
        raise HTTPException(status_code=404, detail="用户不存在")

    try:
        # 获取对应的生成器
        generator_name = template.generator_module
        if not generator_name:
            api_logger.error(f"模板未配置生成器：template_id={request.template_id}")
            raise HTTPException(status_code=500, detail="模板未配置生成器")

        generator = get_generator(generator_name)

        # 调用生成器生成题目（传入 question_type）
        questions = generator.generate(
            template.variables_config,
            request.quantity,
            template.question_type
        )

        if not questions:
            api_logger.error(f"题目生成失败：template_id={request.template_id}")
            raise HTTPException(status_code=500, detail="题目生成失败")

        # 构建响应元数据
        meta = {
            "subject": template.subject,
            "grade": template.grade,
            "title": template.name,
        }

        api_logger.info(f"模板题目生成成功，email: {email}, 题目数：{len(questions)}")

        return TemplateGenerateResponse(
            meta=meta,
            questions=questions,
        )

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"模板题目生成失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
