"""
题目模板 API 接口
"""
import traceback
import json
import sqlite3
from typing import Optional, List, Dict
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
    create_template,
    update_template,
    delete_template,
)
from services.template.generators import get_generator
from api.v1.auth import get_current_user_email
from services.user.user_store import get_user as get_user_by_email
from utils.logger import api_logger
from config import DB_PATH

router = APIRouter(prefix="/api/templates", tags=["templates"])


class TemplateListItem(BaseModel):
    """模板列表项"""
    id: int
    name: str
    subject: str
    grade: str
    semester: str
    textbook_version: str
    example: Optional[str]


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    templates: List[TemplateListItem]


class TemplateGenerateResponse(BaseModel):
    """模板生成题目响应"""
    meta: Dict = Field(..., description="元数据")
    questions: List[Dict] = Field(..., description="题目列表")


class TemplateCreateInput(BaseModel):
    """创建模板输入"""
    name: str
    subject: str
    grade: str
    semester: str
    textbook_version: str
    question_type: str
    template_pattern: str
    variables_config: str  # JSON 字符串格式
    example: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    generator_module: Optional[str] = None


class TemplateUpdateInput(BaseModel):
    """更新模板输入"""
    name: Optional[str] = None
    template_pattern: Optional[str] = None
    variables_config: Optional[str] = None  # JSON 字符串格式
    example: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class TemplateCreateResponse(BaseModel):
    """创建模板响应"""
    id: int


class TemplateMessageResponse(BaseModel):
    """消息响应"""
    message: str


class TemplateTestRequest(BaseModel):
    """测试模板请求"""
    template_id: int
    quantity: int = Field(default=5, ge=1, le=100)


class TemplateTestResponse(BaseModel):
    """测试模板响应"""
    meta: Dict = Field(..., description="元数据")
    questions: List[Dict] = Field(..., description="题目列表")


class TemplateFull(BaseModel):
    """完整模板信息（管理后台用）"""
    id: int
    name: str
    subject: str
    grade: str
    semester: str
    textbook_version: str
    question_type: str
    template_pattern: str
    variables_config: dict
    example: Optional[str]
    generator_module: Optional[str]
    sort_order: int
    is_active: bool
    created_at: str
    updated_at: str


class TemplateAllResponse(BaseModel):
    """所有模板响应（含未启用）"""
    templates: List[TemplateFull]


@router.get("/list", response_model=TemplateListResponse)
async def get_templates(
    grade: str = None,
    subject: str = None,
    semester: str = None,
    textbook_version: str = None,
):
    """
    获取所有启用的模板列表

    返回精简版模板信息，用于前端下拉选择

    筛选参数：
    - grade: 年级 (grade1, grade2, ...)
    - subject: 学科 (math, chinese, english)
    - semester: 学期 (upper, lower)
    - textbook_version: 教材版本 (人教版，北师大版，...)
    """
    api_logger.info(f"获取模板列表请求，筛选条件：grade={grade}, subject={subject}, semester={semester}, textbook_version={textbook_version}")

    try:
        # 获取所有启用的模板
        templates = get_template_list_items()

        # 前端筛选（如果提供了筛选条件）
        if grade or subject or semester or textbook_version:
            filtered = []
            for t in templates:
                if grade and t.grade != grade:
                    continue
                if subject and t.subject != subject:
                    continue
                if semester and t.semester != semester:
                    continue
                if textbook_version and t.textbook_version != textbook_version:
                    continue
                filtered.append(t)
            templates = filtered

        return TemplateListResponse(
            templates=[
                TemplateListItem(
                    id=t.id,
                    name=t.name,
                    subject=t.subject,
                    grade=t.grade,
                    semester=t.semester,
                    textbook_version=t.textbook_version,
                    example=t.example,
                )
                for t in templates
            ]
        )
    except Exception as e:
        api_logger.error(f"获取模板列表失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/all", response_model=TemplateAllResponse)
async def get_all_templates_for_admin():
    """
    获取所有模板（含未启用）- 管理后台专用
    """
    api_logger.info("获取所有模板请求（管理后台）")

    try:
        # 直接查数据库所有记录（包括未启用的）
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT id, name, subject, grade, semester, textbook_version, question_type, template_pattern,
                   variables_config, example, generator_module, sort_order, is_active,
                   created_at, updated_at
            FROM question_templates
            ORDER BY sort_order ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        templates = []
        for row in rows:
            templates.append(TemplateFull(
                id=row["id"],
                name=row["name"],
                subject=row["subject"],
                grade=row["grade"],
                semester=row["semester"],
                textbook_version=row["textbook_version"],
                question_type=row["question_type"],
                template_pattern=row["template_pattern"],
                variables_config=json.loads(row["variables_config"]),
                example=row["example"],
                generator_module=row["generator_module"],
                sort_order=row["sort_order"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            ))

        return TemplateAllResponse(templates=templates)
    except Exception as e:
        api_logger.error(f"获取所有模板失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/create", response_model=TemplateCreateResponse)
async def create_template_api(input: TemplateCreateInput):
    """
    创建新模板 - 管理后台专用
    """
    api_logger.info(f"创建模板请求：name={input.name}")

    try:
        template_id = create_template(
            name=input.name,
            subject=input.subject,
            grade=input.grade,
            semester=input.semester,
            textbook_version=input.textbook_version,
            question_type=input.question_type,
            template_pattern=input.template_pattern,
            variables_config=input.variables_config,
            example=input.example,
            sort_order=input.sort_order,
            is_active=input.is_active,
        )
        return TemplateCreateResponse(id=template_id)
    except Exception as e:
        api_logger.error(f"创建模板失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/{template_id}/update", response_model=TemplateMessageResponse)
async def update_template_api(template_id: int, input: TemplateUpdateInput):
    """
    更新模板 - 管理后台专用
    """
    api_logger.info(f"更新模板请求：id={template_id}")

    try:
        success = update_template(
            template_id=template_id,
            name=input.name,
            template_pattern=input.template_pattern,
            variables_config=input.variables_config,
            example=input.example,
            sort_order=input.sort_order,
            is_active=input.is_active,
        )
        if not success:
            raise HTTPException(status_code=404, detail="模板不存在")
        return TemplateMessageResponse(message="更新成功")
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"更新模板失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/{template_id}/delete", response_model=TemplateMessageResponse)
async def delete_template_api(template_id: int):
    """
    删除模板 - 管理后台专用
    """
    api_logger.info(f"删除模板请求：id={template_id}")

    try:
        success = delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="模板不存在")
        return TemplateMessageResponse(message="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"删除模板失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/{template_id}/toggle", response_model=TemplateMessageResponse)
async def toggle_template_api(template_id: int, is_active: bool = True):
    """
    切换模板启用状态 - 管理后台专用
    """
    api_logger.info(f"切换模板状态请求：id={template_id}, is_active={is_active}")

    try:
        success = update_template(template_id=template_id, is_active=is_active)
        if not success:
            raise HTTPException(status_code=404, detail="模板不存在")
        return TemplateMessageResponse(message="操作成功")
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"切换模板状态失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/{template_id}/test", response_model=TemplateTestResponse)
async def test_template_api(template_id: int, request: TemplateTestRequest):
    """
    测试模板 - 管理后台专用（无需用户登录）
    """
    api_logger.info(f"模板测试请求：template_id={template_id}, quantity={request.quantity}")

    # 获取模板
    template = get_template_by_id(template_id)
    if not template:
        api_logger.warning(f"模板不存在：template_id={template_id}")
        raise HTTPException(status_code=404, detail="模板不存在")

    # 检查模板是否启用
    if not template.is_active:
        api_logger.warning(f"模板未启用：template_id={template_id}")
        raise HTTPException(status_code=400, detail="模板未启用")

    try:
        # 获取对应的生成器
        generator_name = template.generator_module
        if not generator_name:
            api_logger.error(f"模板未配置生成器：template_id={template_id}")
            raise HTTPException(status_code=500, detail="模板未配置生成器")

        generator = get_generator(generator_name)

        # 调用生成器生成题目
        questions = generator.generate(
            template.variables_config,
            request.quantity,
            template.question_type
        )

        if not questions:
            api_logger.error(f"题目生成失败：template_id={template_id}")
            raise HTTPException(status_code=500, detail="题目生成失败")

        # 构建响应元数据
        meta = {
            "subject": template.subject,
            "grade": template.grade,
            "title": template.name,
        }

        api_logger.info(f"模板测试成功：template_id={template_id}, 题目数：{len(questions)}")

        return TemplateTestResponse(
            meta=meta,
            questions=questions,
        )

    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"模板测试失败：{e}")
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
    - quantity: 题目数量（默认 15，范围 5-100）

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
