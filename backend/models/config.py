"""
配置数据模型 - 学科/年级/学期/教材版本/知识点
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 学科模型 ====================

class SubjectBase(BaseModel):
    """学科基础模型"""
    code: str = Field(..., description="学科代码（math/chinese/english）")
    name_zh: str = Field(..., description="学科中文名称")
    sort_order: int = Field(default=0, description="排序序号")


class SubjectCreate(SubjectBase):
    """创建学科请求模型"""
    pass


class SubjectUpdate(BaseModel):
    """更新学科请求模型"""
    name_zh: Optional[str] = Field(None, description="学科中文名称")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_active: Optional[int] = Field(None, description="是否启用（0/1）", ge=0, le=1)


class SubjectInDB(SubjectBase):
    """数据库中学科模型"""
    id: int
    is_active: int = 1
    created_at: str
    updated_at: str


class SubjectResponse(SubjectInDB):
    """学科响应模型"""
    pass


# ==================== 年级模型 ====================

class GradeBase(BaseModel):
    """年级基础模型"""
    code: str = Field(..., description="年级代码（grade1~grade9）")
    name_zh: str = Field(..., description="年级中文名称")
    sort_order: int = Field(default=0, description="排序序号")


class GradeCreate(GradeBase):
    """创建年级请求模型"""
    pass


class GradeUpdate(BaseModel):
    """更新年级请求模型"""
    name_zh: Optional[str] = Field(None, description="年级中文名称")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_active: Optional[int] = Field(None, description="是否启用（0/1）", ge=0, le=1)


class GradeInDB(GradeBase):
    """数据库中学年级模型"""
    id: int
    is_active: int = 1
    created_at: str
    updated_at: str


class GradeResponse(GradeInDB):
    """年级响应模型"""
    pass


# ==================== 学期模型 ====================

class SemesterBase(BaseModel):
    """学期基础模型"""
    code: str = Field(..., description="学期代码（upper/lower）")
    name_zh: str = Field(..., description="学期中文名称")
    sort_order: int = Field(default=0, description="排序序号")


class SemesterCreate(SemesterBase):
    """创建学期请求模型"""
    pass


class SemesterUpdate(BaseModel):
    """更新学期请求模型"""
    name_zh: Optional[str] = Field(None, description="学期中文名称")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_active: Optional[int] = Field(None, description="是否启用（0/1）", ge=0, le=1)


class SemesterInDB(SemesterBase):
    """数据库中学期模型"""
    id: int
    is_active: int = 1
    created_at: str
    updated_at: str


class SemesterResponse(SemesterInDB):
    """学期响应模型"""
    pass


# ==================== 教材版本模型 ====================

class TextbookVersionBase(BaseModel):
    """教材版本基础模型"""
    version_code: str = Field(..., description="教材版本代码（rjb/bsd/sj 等）")
    name_zh: str = Field(..., description="教材版本中文名称")
    sort_order: int = Field(default=0, description="排序序号")


class TextbookVersionCreate(TextbookVersionBase):
    """创建教材版本请求模型"""
    pass


class TextbookVersionUpdate(BaseModel):
    """更新教材版本请求模型"""
    name_zh: Optional[str] = Field(None, description="教材版本中文名称")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_active: Optional[int] = Field(None, description="是否启用（0/1）", ge=0, le=1)


class TextbookVersionInDB(TextbookVersionBase):
    """数据库中教材版本模型"""
    id: int
    is_active: int = 1
    created_at: str
    updated_at: str


class TextbookVersionResponse(TextbookVersionInDB):
    """教材版本响应模型"""
    pass


# ==================== 知识点模型 ====================
# 说明：扁平结构，直接存储学科/年级/学期/教材版本代码

class KnowledgePointBase(BaseModel):
    """知识点基础模型"""
    name: str = Field(..., description="知识点名称")
    subject_code: str = Field(..., description="学科代码")
    grade_code: str = Field(..., description="年级代码")
    semester_code: str = Field(..., description="学期代码")
    textbook_version_code: str = Field(..., description="教材版本代码")
    sort_order: int = Field(default=0, description="排序序号")


class KnowledgePointCreate(KnowledgePointBase):
    """创建知识点请求模型"""
    pass


class KnowledgePointUpdate(BaseModel):
    """更新知识点请求模型"""
    name: Optional[str] = Field(None, description="知识点名称")
    subject_code: Optional[str] = Field(None, description="学科代码")
    grade_code: Optional[str] = Field(None, description="年级代码")
    semester_code: Optional[str] = Field(None, description="学期代码")
    textbook_version_code: Optional[str] = Field(None, description="教材版本代码")
    sort_order: Optional[int] = Field(None, description="排序序号")
    is_active: Optional[int] = Field(None, description="是否启用（0/1）", ge=0, le=1)


class KnowledgePointInDB(KnowledgePointBase):
    """数据库中知识点模型"""
    id: int
    is_active: int = 1
    created_at: str
    updated_at: str


class KnowledgePointResponse(KnowledgePointInDB):
    """知识点响应模型"""
    pass


# ==================== 配置总览响应 ====================

class ConfigOptionsResponse(BaseModel):
    """配置选项响应（用于下拉框）"""
    value: str
    label: str


class TextbookVersionOption(BaseModel):
    """教材版本选项"""
    id: str
    name: str
    sort: int


class QuestionTypeOption(BaseModel):
    """题型选项"""
    value: str
    label: str
    subjects: List[str]


class AllConfigsResponse(BaseModel):
    """所有配置响应"""
    subjects: List[ConfigOptionsResponse]
    grades: List[ConfigOptionsResponse]
    semesters: List[ConfigOptionsResponse]
    textbook_versions: List[TextbookVersionOption]
    question_types: List[QuestionTypeOption]
    generator_modules: List[ConfigOptionsResponse]
