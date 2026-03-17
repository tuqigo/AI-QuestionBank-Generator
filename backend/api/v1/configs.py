"""配置接口 - 提供全局配置常量给前端

改造说明：
- 保留原有的 /api/configs/configs 接口保持向后兼容
- 新增数据库配置数据的 CRUD 接口
- 支持管理后台动态配置学科/年级/学期/教材版本/知识点
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from models.config import (
    # 学科模型
    SubjectCreate, SubjectUpdate, SubjectResponse,
    # 年级模型
    GradeCreate, GradeUpdate, GradeResponse,
    # 学期模型
    SemesterCreate, SemesterUpdate, SemesterResponse,
    # 教材版本模型
    TextbookVersionCreate, TextbookVersionUpdate, TextbookVersionResponse,
    # 知识点模型
    KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointResponse,
    # 通用响应
    AllConfigsResponse, ConfigOptionsResponse, TextbookVersionOption, QuestionTypeOption,
)
from services.config import (
    SubjectStore, GradeStore, SemesterStore, TextbookVersionStore, KnowledgePointStore,
)
from services.question.question_type_store import QuestionTypeStore
from core.constants import SUPPORTED_GENERATOR_MODULES

router = APIRouter()


# ==================== 公共配置接口 ====================

@router.get("/configs", response_model=AllConfigsResponse)
def get_all_configs():
    """获取所有配置常量（保持向后兼容）

    返回格式与原有实现保持一致，支持前端下拉框选择。
    数据来源于数据库，当数据库不可用时 fallback 到 constants.py。
    """
    try:
        # 从数据库加载配置
        subjects = SubjectStore.get_as_options()
        grades = GradeStore.get_as_options()
        semesters = SemesterStore.get_as_options()
        textbook_versions = TextbookVersionStore.get_as_options()
    except Exception:
        # Fallback 到 constants.py
        from core.constants import (
            SUPPORTED_SUBJECTS, SUPPORTED_GRADES, SUPPORTED_SEMESTERS,
            SUPPORTED_TEXTBOOK_VERSIONS, get_textbook_versions_list,
        )
        subjects = [{"value": k, "label": v} for k, v in SUPPORTED_SUBJECTS.items()]
        grades = [{"value": k, "label": v} for k, v in SUPPORTED_GRADES.items()]
        semesters = [{"value": k, "label": v} for k, v in SUPPORTED_SEMESTERS.items()]
        textbook_versions = [
            {"id": vid, "name": vdata["name"], "sort": vdata["sort"]}
            for vid, vdata in sorted(SUPPORTED_TEXTBOOK_VERSIONS.items(),
                                      key=lambda x: x[1]["sort"])
        ]

    # 题型列表（从数据库加载）
    try:
        question_types_db = QuestionTypeStore.get_all_with_subjects()
        question_types = [
            {"value": qt.en_name, "label": qt.zh_name, "subjects": qt.subjects}
            for qt in question_types_db
        ]
    except Exception:
        # Fallback 到 constants.py
        from core.constants import SUPPORTED_QUESTION_TYPES
        question_types = []
        for en_name, (zh_name, qt_subjects) in SUPPORTED_QUESTION_TYPES.items():
            question_types.append({
                "value": en_name,
                "label": zh_name,
                "subjects": qt_subjects
            })

    # 生成器模块列表（保持常量）
    generator_modules = [
        {"value": k, "label": v}
        for k, v in SUPPORTED_GENERATOR_MODULES.items()
    ]

    return {
        "subjects": [ConfigOptionsResponse(**s) for s in subjects],
        "grades": [ConfigOptionsResponse(**g) for g in grades],
        "semesters": [ConfigOptionsResponse(**s) for s in semesters],
        "textbook_versions": [TextbookVersionOption(**tv) for tv in textbook_versions],
        "question_types": [QuestionTypeOption(**qt) for qt in question_types],
        "generator_modules": [ConfigOptionsResponse(**gm) for gm in generator_modules],
    }


# ==================== 学科管理接口 ====================

@router.get("/subjects", response_model=List[SubjectResponse])
def list_subjects(active_only: bool = True):
    """获取学科列表"""
    return SubjectStore.get_all(active_only=active_only)


@router.post("/admin/subjects/create", response_model=SubjectResponse)
def create_subject(input_data: SubjectCreate):
    """创建学科（管理端）"""
    # 检查 code 是否已存在
    existing = SubjectStore.get_by_code(input_data.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"学科代码 '{input_data.code}' 已存在")

    return SubjectStore.create(input_data)


@router.put("/admin/subjects/{id}/update", response_model=SubjectResponse)
def update_subject(id: int, input_data: SubjectUpdate):
    """更新学科（管理端）"""
    result = SubjectStore.update(id, input_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"学科 ID {id} 不存在")
    return result


@router.delete("/admin/subjects/{id}/delete")
def delete_subject(id: int):
    """删除学科（软删除，管理端）"""
    success = SubjectStore.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail=f"学科 ID {id} 不存在")
    return {"message": "删除成功"}


# ==================== 年级管理接口 ====================

@router.get("/grades", response_model=List[GradeResponse])
def list_grades(active_only: bool = True):
    """获取年级列表"""
    return GradeStore.get_all(active_only=active_only)


@router.post("/admin/grades/create", response_model=GradeResponse)
def create_grade(input_data: GradeCreate):
    """创建年级（管理端）"""
    # 检查 code 是否已存在
    existing = GradeStore.get_by_code(input_data.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"年级代码 '{input_data.code}' 已存在")

    return GradeStore.create(input_data)


@router.put("/admin/grades/{id}/update", response_model=GradeResponse)
def update_grade(id: int, input_data: GradeUpdate):
    """更新年级（管理端）"""
    result = GradeStore.update(id, input_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"年级 ID {id} 不存在")
    return result


@router.delete("/admin/grades/{id}/delete")
def delete_grade(id: int):
    """删除年级（软删除，管理端）"""
    success = GradeStore.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail=f"年级 ID {id} 不存在")
    return {"message": "删除成功"}


# ==================== 学期管理接口 ====================

@router.get("/semesters", response_model=List[SemesterResponse])
def list_semesters(active_only: bool = True):
    """获取学期列表"""
    return SemesterStore.get_all(active_only=active_only)


@router.post("/admin/semesters/create", response_model=SemesterResponse)
def create_semester(input_data: SemesterCreate):
    """创建学期（管理端）"""
    # 检查 code 是否已存在
    existing = SemesterStore.get_by_code(input_data.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"学期代码 '{input_data.code}' 已存在")

    return SemesterStore.create(input_data)


@router.put("/admin/semesters/{id}/update", response_model=SemesterResponse)
def update_semester(id: int, input_data: SemesterUpdate):
    """更新学期（管理端）"""
    result = SemesterStore.update(id, input_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"学期 ID {id} 不存在")
    return result


@router.delete("/admin/semesters/{id}/delete")
def delete_semester(id: int):
    """删除学期（软删除，管理端）"""
    success = SemesterStore.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail=f"学期 ID {id} 不存在")
    return {"message": "删除成功"}


# ==================== 教材版本管理接口 ====================

@router.get("/textbook-versions", response_model=List[TextbookVersionResponse])
def list_textbook_versions(active_only: bool = True):
    """获取教材版本列表"""
    return TextbookVersionStore.get_all(active_only=active_only)


@router.post("/admin/textbook-versions/create", response_model=TextbookVersionResponse)
def create_textbook_version(input_data: TextbookVersionCreate):
    """创建教材版本（管理端）"""
    # 检查 code 是否已存在
    existing = TextbookVersionStore.get_by_code(input_data.version_code)
    if existing:
        raise HTTPException(status_code=400, detail=f"教材版本代码 '{input_data.version_code}' 已存在")

    return TextbookVersionStore.create(input_data)


@router.put("/admin/textbook-versions/{id}/update", response_model=TextbookVersionResponse)
def update_textbook_version(id: int, input_data: TextbookVersionUpdate):
    """更新教材版本（管理端）"""
    result = TextbookVersionStore.update(id, input_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"教材版本 ID {id} 不存在")
    return result


@router.delete("/admin/textbook-versions/{id}/delete")
def delete_textbook_version(id: int):
    """删除教材版本（软删除，管理端）"""
    success = TextbookVersionStore.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail=f"教材版本 ID {id} 不存在")
    return {"message": "删除成功"}


# ==================== 知识点管理接口 ====================

@router.get("/knowledge-points", response_model=List[KnowledgePointResponse])
def list_knowledge_points(
    subject_code: Optional[str] = None,
    grade_code: Optional[str] = None,
    semester_code: Optional[str] = None,
    textbook_version_code: Optional[str] = None,
    active_only: bool = True,
):
    """获取知识点列表（可按条件筛选）"""
    return KnowledgePointStore.get_by_filters(
        subject_code=subject_code,
        grade_code=grade_code,
        semester_code=semester_code,
        textbook_version_code=textbook_version_code,
        active_only=active_only,
    )


@router.post("/admin/knowledge-points/create", response_model=KnowledgePointResponse)
def create_knowledge_point(input_data: KnowledgePointCreate):
    """创建知识点（管理端）"""
    return KnowledgePointStore.create(input_data)


@router.put("/admin/knowledge-points/{id}/update", response_model=KnowledgePointResponse)
def update_knowledge_point(id: int, input_data: KnowledgePointUpdate):
    """更新知识点（管理端）"""
    result = KnowledgePointStore.update(id, input_data)
    if not result:
        raise HTTPException(status_code=404, detail=f"知识点 ID {id} 不存在")
    return result


@router.delete("/admin/knowledge-points/{id}/delete")
def delete_knowledge_point(id: int):
    """删除知识点（软删除，管理端）"""
    success = KnowledgePointStore.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail=f"知识点 ID {id} 不存在")
    return {"message": "删除成功"}
