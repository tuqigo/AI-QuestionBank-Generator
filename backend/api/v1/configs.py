"""配置接口 - 提供全局配置常量给前端"""
from fastapi import APIRouter
from core.constants import (
    SUPPORTED_SUBJECTS,
    SUPPORTED_GRADES,
    SUPPORTED_SEMESTERS,
    SUPPORTED_TEXTBOOK_VERSIONS,
    SUPPORTED_QUESTION_TYPES,
    SUPPORTED_GENERATOR_MODULES,
    get_textbook_versions_list,
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

    # 构建生成器模块列表
    generator_modules = [
        {"value": k, "label": v}
        for k, v in SUPPORTED_GENERATOR_MODULES.items()
    ]

    # 教材版本：返回 ID 和名称映射
    textbook_versions = [
        {"id": vid, "name": vdata["name"], "sort": vdata["sort"]}
        for vid, vdata in sorted(SUPPORTED_TEXTBOOK_VERSIONS.items(),
                                  key=lambda x: x[1]["sort"])
    ]

    return {
        "subjects": [{"value": k, "label": v} for k, v in SUPPORTED_SUBJECTS.items()],
        "grades": [{"value": k, "label": v} for k, v in SUPPORTED_GRADES.items()],
        "semesters": [{"value": k, "label": v} for k, v in SUPPORTED_SEMESTERS.items()],
        "textbook_versions": textbook_versions,
        "question_types": question_types,
        "generator_modules": generator_modules,
    }
