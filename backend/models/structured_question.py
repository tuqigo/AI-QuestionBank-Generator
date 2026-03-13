"""
结构化题目数据模型
用于 AI 生成题目的结构化数据解析和校验
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


# ===================== 题型定义 =====================

class BaseQuestion(BaseModel):
    """题目基类"""
    type: str = Field(description="题型")
    stem: str = Field(description="题干内容（支持LaTeX公式）")
    knowledge_points: List[str] = Field(
        description="知识点列表",
        min_items=1
    )


class QuestionWithOptions(BaseQuestion):
    """带选项的题目（单选题、多选题）"""
    options: List[str] = Field(
        description="选项数组（SINGLE_CHOICE必须4个，MULTIPLE_CHOICE至少2个）",
        min_items=2
    )


class QuestionWithPassage(BaseQuestion):
    """带阅读材料的题目（阅读理解、完形填空）"""
    passage: str = Field(description="阅读材料或完形原文")


class QuestionWithSubQuestions(BaseQuestion):
    """带子题的题目（阅读理解、完形填空）"""
    sub_questions: List["Question"] = Field(
        description="子题目列表",
        min_items=1
    )


# 定义完整的 Question 模型（使用更新后的定义）
class Question(BaseModel):
    """
    题目模型 - 支持 11 种题型

    题型分类：
    1. SINGLE_CHOICE - 单选题（必须4个选项）
    2. MULTIPLE_CHOICE - 多选题（至少2个选项）
    3. TRUE_FALSE - 判断题
    4. FILL_BLANK - 填空题
    5. CALCULATION - 计算题
    6. WORD_PROBLEM - 应用题
    7. GEOMETRY - 几何题
    8. READ_COMP - 阅读理解（带 passage 和 sub_questions）
    9. POETRY_APP - 古诗文鉴赏/默写
    10. CLOZE - 完形填空（带 passage 和 sub_questions）
    11. ESSAY - 作文题
    """
    type: str = Field(
        description="题型枚举",
        example="SINGLE_CHOICE"
    )
    stem: str = Field(description="题干内容")
    knowledge_points: List[str] = Field(min_items=1)

    # 可选字段
    options: Optional[List[str]] = Field(
        default=None,
        description="选项（仅 SINGLE_CHOICE 和 MULTIPLE_CHOICE 有）"
    )
    passage: Optional[str] = Field(
        default=None,
        description="阅读材料（仅 READ_COMP 和 CLOZE 有）"
    )
    sub_questions: Optional[List["Question"]] = Field(
        default=None,
        description="子题目（仅 READ_COMP 和 CLOZE 有）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "SINGLE_CHOICE",
                "stem": "下列各数中，属于负有理数的是",
                "options": ["A. $3$", "B. $0$", "C. $-\\sqrt{2}$", "D. $-0.5$"],
                "knowledge_points": ["有理数的概念"]
            }
        }


class MetaData(BaseModel):
    """元数据"""
    subject: str = Field(
        description="学科：math, chinese, english",
        example="math"
    )
    grade: str = Field(
        description="年级：grade1 ~ grade9",
        example="grade7"
    )
    title: str = Field(
        description="试卷标题",
        example="初一数学综合练习题"
    )


class QuestionBank(BaseModel):
    """题库模型 - AI 返回的完整结构"""
    meta: MetaData = Field(description="元数据")
    questions: List[Question] = Field(
        description="题目列表",
        min_items=1
    )


# ===================== API 请求/响应模型 =====================

class StructuredGenerateRequest(BaseModel):
    """结构化题目生成请求"""
    prompt: str = Field(description="用户提示词")


class StructuredQuestionResponse(BaseModel):
    """单个结构化题目响应（含后端填充字段）"""
    type: str
    stem: str
    knowledge_points: List[str]
    options: Optional[List[str]]
    passage: Optional[str]
    sub_questions: Optional[List["StructuredQuestionResponse"]]
    rows_to_answer: int = Field(
        description="预留作答行数（后端自动计算填充）"
    )


class StructuredGenerateResponse(BaseModel):
    """结构化题目生成响应"""
    meta: MetaData
    questions: List[StructuredQuestionResponse]
    record_id: Optional[int] = None
    short_id: Optional[str] = None
    created_at: Optional[datetime] = None


# 更新 Question 模型的引用（解决循环引用问题）
StructuredQuestionResponse.update_forward_refs()


# ===================== 辅助函数 =====================

def calculate_rows_to_answer(question: Union[dict, Question]) -> int:
    """
    计算题目预留作答行数

    规则：
    - SINGLE_CHOICE / TRUE_FALSE / FILL_BLANK / POETRY_APP / ESSAY: 1-5 行
    - CALCULATION / WORD_PROBLEM / GEOMETRY: 3 行
    - READ_COMP / CLOZE: 题干行数 + 子题数 × 2
    """
    # 处理 Pydantic model 或 dict
    q_type = question.type if isinstance(question, Question) else question.get("type", "")

    # 基础题型：1-3 行
    basic_rows = {
        "SINGLE_CHOICE": 1,
        "TRUE_FALSE": 1,
        "FILL_BLANK": 1,
        "CALCULATION": 3,
        "WORD_PROBLEM": 3,
        "GEOMETRY": 3,
        "POETRY_APP": 3,
        "ESSAY": 5,
    }

    if q_type in basic_rows:
        return basic_rows[q_type]

    # 阅读理解/完形填空：题干行数 + 子题数 × 2
    if q_type in ["READ_COMP", "CLOZE"]:
        passage = question.passage if isinstance(question, Question) else question.get("passage", "")
        passage_lines = len(passage.split("\n")) if passage else 1
        sub_questions = question.sub_questions if isinstance(question, Question) else question.get("sub_questions", [])
        sub_questions_count = len(sub_questions) if sub_questions else 0
        return passage_lines + sub_questions_count * 2

    # 默认 1 行
    return 1

