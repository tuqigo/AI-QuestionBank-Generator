"""
项目全局配置常量
所有学科、年级、学期、教材版本、题型等配置在此统一维护
"""
from typing import Dict, List

# ==================== 学科配置 ====================
SUPPORTED_SUBJECTS: Dict[str, str] = {
    "math": "数学",
    "chinese": "语文",
    "english": "英语",
}

# ==================== 年级配置 ====================
SUPPORTED_GRADES: Dict[str, str] = {
    "grade1": "一年级",
    "grade2": "二年级",
    "grade3": "三年级",
    "grade4": "四年级",
    "grade5": "五年级",
    "grade6": "六年级",
    "grade7": "七年级",
    "grade8": "八年级",
    "grade9": "九年级",
}

# ==================== 学期配置 ====================
SUPPORTED_SEMESTERS: Dict[str, str] = {
    "upper": "上学期",
    "lower": "下学期",
}

# ==================== 教材版本配置 ====================
SUPPORTED_TEXTBOOK_VERSIONS: List[str] = [
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

# ==================== 题型配置 ====================
# 题型与学科映射关系：key 为题型英文名，value 为 (中文名称，适用学科列表)
SUPPORTED_QUESTION_TYPES: Dict[str, tuple] = {
    # 通用题型（语/数/英全学科适用）
    "SINGLE_CHOICE": ("单选题", ["math", "chinese", "english"]),
    "MULTIPLE_CHOICE": ("多选题", ["math", "chinese", "english"]),
    "TRUE_FALSE": ("判断题", ["math", "chinese", "english"]),
    "FILL_BLANK": ("填空题", ["math", "chinese", "english"]),

    # 数学专属题型
    "CALCULATION": ("计算题", ["math"]),
    "WORD_PROBLEM": ("应用题", ["math"]),
    "ORAL_CALCULATION": ("口算题", ["math"]),

    # 语文 + 英语通用专属题型
    "READ_COMP": ("阅读理解", ["chinese", "english"]),
    "ESSAY": ("作文/书面表达", ["chinese", "english"]),
    "CLOZE": ("完形填空", ["english"]),
}
