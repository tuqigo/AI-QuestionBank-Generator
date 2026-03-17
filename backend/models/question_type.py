from typing import List, Optional
from pydantic import BaseModel, field_validator


class QuestionTypeBase(BaseModel):
    """题型基础模型"""
    en_name: str
    zh_name: str


class QuestionTypeCreate(BaseModel):
    """创建题型请求模型"""
    en_name: str
    zh_name: str
    subjects: List[str] = ["math", "chinese", "english"]


class QuestionTypeUpdate(BaseModel):
    """更新题型请求模型"""
    zh_name: Optional[str] = None
    subjects: Optional[List[str]] = None
    is_active: Optional[int] = None


class QuestionTypeInDB(BaseModel):
    """数据库中的题型模型"""
    id: int
    en_name: str
    zh_name: str
    subjects: List[str]  # 数据库中是逗号分隔的字符串，validator 会解析为列表
    is_active: int = 1
    created_at: str
    updated_at: str

    @field_validator('subjects', mode='before')
    @classmethod
    def parse_subjects(cls, v):
        """将逗号分隔的字符串转换为列表"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [s.strip() for s in v.split(',') if s.strip()]
        return ["math", "chinese", "english"]


class QuestionTypeResponse(QuestionTypeInDB):
    """题型响应模型"""
    pass


class QuestionTypeListResponse(BaseModel):
    """题型列表响应模型"""
    total: int
    items: List[QuestionTypeResponse]


# 题型常量定义
class QuestionTypeEnum:
    """题型枚举常量"""
    # 通用题型（语/数/英全学科适用）
    SINGLE_CHOICE = "SINGLE_CHOICE"  # 单选题
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"  # 多选题
    TRUE_FALSE = "TRUE_FALSE"  # 判断题
    FILL_BLANK = "FILL_BLANK"  # 填空题

    # 数学专属题型
    CALCULATION = "CALCULATION"  # 计算题/解方程/脱式计算
    WORD_PROBLEM = "WORD_PROBLEM"  # 应用题
    ORAL_CALCULATION = "ORAL_CALCULATION"  # 口算题

    # 语文 + 英语通用专属题型
    READ_COMP = "READ_COMP"  # 阅读理解
    ESSAY = "ESSAY"  # 作文/书面表达
    CLOZE = "CLOZE"  # 完形填空
