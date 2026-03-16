"""配置接口 - 提供全局配置常量给前端"""
from fastapi import APIRouter
from core.constants import (
    SUPPORTED_SUBJECTS,
    SUPPORTED_GRADES,
    SUPPORTED_SEMESTERS,
    SUPPORTED_TEXTBOOK_VERSIONS,
)

router = APIRouter()


@router.get("/configs")
def get_all_configs():
    """获取所有配置常量"""
    return {
        "subjects": [{"value": k, "label": v} for k, v in SUPPORTED_SUBJECTS.items()],
        "grades": [{"value": k, "label": v} for k, v in SUPPORTED_GRADES.items()],
        "semesters": [{"value": k, "label": v} for k, v in SUPPORTED_SEMESTERS.items()],
        "textbook_versions": SUPPORTED_TEXTBOOK_VERSIONS,
    }
