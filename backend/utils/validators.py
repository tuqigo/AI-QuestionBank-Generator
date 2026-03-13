"""提示词校验工具函数"""

from typing import Optional

# 年级关键词列表
GRADE_KEYWORDS = [
    "一年级", "二年级", "三年级", "四年级", "五年级", "六年级",
    "七年级", "八年级", "九年级",
    "初一", "初二", "初三"
]

# 学科关键词列表
SUBJECT_KEYWORDS = [
    "数学", "语文", "英语", "科学",
    "物理", "化学", "生物", "历史", "地理", "政治"
]

# 校验规则常量
MIN_LENGTH = 5
MAX_LENGTH = 200


def validate_prompt(prompt: str) -> Optional[str]:
    """
    校验提示词

    Args:
        prompt: 用户输入的提示词

    Returns:
        如果校验失败返回错误信息，成功返回 None
    """
    # 空值校验
    if not prompt or not prompt.strip():
        return "请输入题目要求"

    p = prompt.strip()

    # 最小长度校验
    if len(p) < MIN_LENGTH:
        return f"题目要求太短，请至少输入 {MIN_LENGTH} 个字"

    # 最大长度校验
    if len(p) > MAX_LENGTH:
        return f"题目要求太长，请精简到 {MAX_LENGTH} 字以内"

    # 必需元素校验：必须包含年级或学科关键词
    has_grade = any(keyword in p for keyword in GRADE_KEYWORDS)
    has_subject = any(keyword in p for keyword in SUBJECT_KEYWORDS)

    if not has_grade and not has_subject:
        return "请说明年级和学科（如：三年级数学，初三英语）"

    return None


def is_valid_prompt(prompt: str) -> bool:
    """
    检查提示词是否有效

    Args:
        prompt: 用户输入的提示词

    Returns:
        True 表示有效，False 表示无效
    """
    return validate_prompt(prompt) is None
