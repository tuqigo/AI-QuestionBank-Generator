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


# ===================== 规则约束 =====================

# 支持的规则列表
# 按功能分类，便于生成器按需使用
SUPPORTED_RULES = {
    # ===================== 数值范围约束 =====================
    "result_within_10",       # 确保结果 ≤ 10（一年级）
    "result_within_20",       # 确保结果 ≤ 20（二年级）
    "result_within_100",      # 确保结果 ≤ 100（三年级）
    "result_within_1000",     # 确保结果 ≤ 1000（四年级）

    # ===================== 数值属性约束 =====================
    "ensure_different",       # 确保两个数不同（用于比大小）
    "ensure_positive",        # 确保减法结果不为负数
    "ensure_non_zero",        # 确保不为零（用于除法、分母）
    "ensure_even",            # 确保是偶数
    "ensure_odd",             # 确保是奇数
    "ensure_prime",           # 确保是质数
    "ensure_coprime",         # 确保互质（用于分数约分）

    # ===================== 运算约束 =====================
    "ensure_divisible",       # 确保除法能整除
    "ensure_no_remainder",    # 确保除法无余数
    "ensure_borrowing",       # 确保减法需要借位
    "ensure_carrying",        # 确保加法需要进位

    # ===================== 分数相关约束 =====================
    "ensure_proper_fraction",  # 确保是真分数（分子 < 分母）
    "ensure_simplest_form",   # 确保是最简分数
    "ensure_common_denominator",  # 确保同分母

    # ===================== 几何/单位约束 =====================
    "ensure_realistic_value",  # 确保是实际存在的值（如长度为正）
    "ensure_integer_result",  # 确保计算结果为整数

    # ===================== 去重约束 =====================
    "ensure_unique_stem",     # 确保题干不重复（默认开启）
}


# ===================== 教材版本 =====================

# 支持的教材版本列表
SUPPORTED_TEXTBOOK_VERSIONS = [
    "人教版",
    "人教版 (新)",
    "北师大版",
    "苏教版",
    "西师版",
    "沪教版",
    "北京版",
    "青岛六三",
    "青岛五四",
]

# 支持的学期
SUPPORTED_SEMESTERS = {
    "upper": "上学期",
    "lower": "下学期",
}


# ===================== 模板模型 =====================

class QuestionTemplate(BaseModel):
    """题目模板模型"""
    id: Optional[int] = Field(None, description="模板 ID")
    name: str = Field(..., description="模板名称")
    subject: str = Field(..., description="学科：math/chinese/english")
    grade: str = Field(..., description="年级：grade1~grade9")
    semester: str = Field(..., description="学期：upper/lower (上学期/下学期)")
    textbook_version: str = Field(..., description="教材版本：人教版/人教版 (新)/北师大版/苏教版/西师版/沪教版/北京版/青岛六三/青岛五四")
    question_type: str = Field(..., description="题型")
    template_pattern: str = Field(..., description="模板模式字符串")
    variables_config: dict = Field(..., description="变量配置")
    example: Optional[str] = Field(None, description="示例")
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
                "question_type": "CALCULATION",
                "template_pattern": "{a} {op} {b} = （ ）",
                "variables_config": {
                    "a": {"min": 1, "max": 10},
                    "b": {"min": 1, "max": 10},
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
    example: Optional[str]
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
