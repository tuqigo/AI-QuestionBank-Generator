"""
项目全局配置常量
所有学科、年级、学期、教材版本等配置在此统一维护
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
