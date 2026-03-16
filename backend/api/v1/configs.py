"""配置接口 - 提供全局配置常量给前端"""
from fastapi import APIRouter
from core.constants import (
    SUPPORTED_SUBJECTS,
    SUPPORTED_GRADES,
    SUPPORTED_SEMESTERS,
    SUPPORTED_TEXTBOOK_VERSIONS,
    SUPPORTED_QUESTION_TYPES,
)

router = APIRouter()


@router.get("/configs")
def get_all_configs():
    """获取所有配置常量"""
    # 构建题型列表（带学科映射）
    question_types = []
    for en_name, (zh_name, subjects) in SUPPORTED_QUESTION_TYPES.items():
        question_types.append({
            "value": en_name,
            "label": zh_name,
            "subjects": subjects
        })

    return {
        "subjects": [{"value": k, "label": v} for k, v in SUPPORTED_SUBJECTS.items()],
        "grades": [{"value": k, "label": v} for k, v in SUPPORTED_GRADES.items()],
        "semesters": [{"value": k, "label": v} for k, v in SUPPORTED_SEMESTERS.items()],
        "textbook_versions": SUPPORTED_TEXTBOOK_VERSIONS,
        "question_types": question_types,
    }
