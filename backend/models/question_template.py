"""
题目模板数据模型
用于模板配置和题目生成
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===================== 变量配置模型 =====================

class VariableRange(BaseModel):
    """数值变量范围配置"""
    min: int = Field(description="最小值")
    max: int = Field(description="最大值")


class VariableValues(BaseModel):
    """枚举变量配置"""
    values: List[str] = Field(description="可选值列表")


class TemplateVariablesConfig(BaseModel):
    """
    模板变量配置

    示例：
    {
        "a": {"min": 1, "max": 10},
        "b": {"min": 1, "max": 10},
        "op": {"values": ["+", "-"]},
        "rules": ["ensure_positive"]
    }
    """
    # 动态字段，通过 config.extra 允许额外字段
    rules: List[str] = Field(default_factory=list, description="规则约束列表")

    class Config:
        extra = "allow"  # 允许额外字段（a, b, op 等变量）


# ===================== 模板模型 =====================

class QuestionTemplate(BaseModel):
    """题目模板模型"""
    id: Optional[int] = Field(None, description="模板 ID")
    name: str = Field(..., description="模板名称")
    subject: str = Field(..., description="学科（见 core.constants.SUPPORTED_SUBJECTS）")
    grade: str = Field(..., description="年级（见 core.constants.SUPPORTED_GRADES）")
    semester: str = Field(..., description="学期（见 core.constants.SUPPORTED_SEMESTERS）")
    textbook_version: str = Field(..., description="教材版本（见 core.constants.SUPPORTED_TEXTBOOK_VERSIONS）")
    question_type: str = Field(..., description="题型（见 core.constants.SUPPORTED_QUESTION_TYPES）")
    template_pattern: Optional[str] = Field(None, description="模板模式字符串")
    variables_config: Optional[dict] = Field(None, description="变量配置")
    knowledge_point_id: Optional[int] = Field(None, description="关联 knowledge_points 表的 ID")
    description: Optional[str] = Field(None, description="模板描述")
    example: Optional[List[str]] = Field(None, description="示例题目数组")
    generator_module: Optional[str] = Field(None, description="生成器模块名")
    sort_order: int = Field(0, description="排序序号")
    is_active: bool = Field(True, description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "一年级 10 以内的加减法",
                "subject": "math",
                "grade": "grade1",
                "semester": "lower",
                "textbook_version": "沪教版",
                "question_type": "CALCULATION",
                "template_pattern": "{a} {op} {b} = （ ）",
                "variables_config": {
                    "num": {"min": 1, "max": 10},
                    "op": {"values": ["+", "-"]},
                    "rules": ["ensure_positive"]
                },
                "example": "2 + 2 = （ ）",
                "sort_order": 1,
                "is_active": True
            }
        }


class QuestionTemplateListItem(BaseModel):
    """模板列表项（精简版，用于前端下拉选择）"""
    id: int
    name: str
    subject: str
    grade: str
    semester: str
    textbook_version: str
    question_type: str
    knowledge_point_id: Optional[int]
    description: Optional[str]
    example: Optional[List[str]]
    sort_order: int


class QuestionTemplateListResponse(BaseModel):
    """模板列表响应"""
    templates: List[QuestionTemplateListItem]


# ===================== 题目生成请求/响应 =====================

class TemplateGenerateRequest(BaseModel):
    """根据模板生成题目请求"""
    template_id: int = Field(..., description="模板 ID")
    quantity: int = Field(15, description="题目数量", ge=5, le=100)


class TemplateGenerateResponse(BaseModel):
    """根据模板生成题目响应"""
    meta: dict = Field(..., description="元数据")
    questions: List[dict] = Field(..., description="题目列表")
    record_id: int = Field(..., description="记录 ID")
    short_id: str = Field(..., description="短 ID")
