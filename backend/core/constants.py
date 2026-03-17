"""
项目全局配置常量
所有学科、年级、学期、教材版本、题型等配置在此统一维护
"""
from typing import Dict, List, TypedDict

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
# 使用 ID 化设计，方便未来修改版本名称而不影响数据库
# 格式：{id: {name: "显示名称", sort: 排序序号}}
SUPPORTED_TEXTBOOK_VERSIONS: Dict[str, Dict[str, int]] = {
    "rjb": {"name": "人教版", "sort": 1},
    "rjb_2024": {"name": "人教版（2024 新版）", "sort": 2},
    "rjb_xin": {"name": "人教版 (新)", "sort": 3},
    "bsd": {"name": "北师大版", "sort": 4},
    "sj": {"name": "苏教版", "sort": 5},
    "xs": {"name": "西师版", "sort": 6},
    "hj": {"name": "沪教版", "sort": 7},
    "bj": {"name": "北京版", "sort": 8},
    "qd_ll": {"name": "青岛六三", "sort": 9},
    "qd_sw": {"name": "青岛五四", "sort": 10},
}

# 辅助函数：获取教材版本列表（按 sort 排序）
def get_textbook_versions_list() -> List[str]:
    """返回按 sort 排序后的教材版本 ID 列表"""
    return sorted(SUPPORTED_TEXTBOOK_VERSIONS.keys(),
                  key=lambda x: SUPPORTED_TEXTBOOK_VERSIONS[x]["sort"])

# 辅助函数：根据 ID 获取教材版本名称
def get_textbook_version_name(version_id: str) -> str:
    """根据版本 ID 获取显示名称"""
    return SUPPORTED_TEXTBOOK_VERSIONS.get(version_id, {}).get("name", version_id)

# 辅助函数：根据名称获取教材版本 ID（反向查找）
def get_textbook_version_id(name: str) -> str:
    """根据显示名称获取版本 ID"""
    for vid, vdata in SUPPORTED_TEXTBOOK_VERSIONS.items():
        if vdata["name"] == name:
            return vid
    return name  # 如果找不到，返回原值（兼容旧数据）

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

# ==================== 生成器模块配置 ====================
# key 为生成器模块名，value 为中文名称
SUPPORTED_GENERATOR_MODULES: Dict[str, str] = {
    "compare_number": "数字比较",
    "currency_conversion": "货币转换",
    "volume_conversion": "体积转换",
    "fraction_comparison": "分数比较",
    "mixed_addition_subtraction": "加减混合运算",
    "length_comparison": "长度比较",
    "multiplication_division_comprehensive": "乘除综合",
}

# ==================== 知识点分组配置 ====================
# 按学科 -> 年级 -> 学期 -> 教材版本 组织知识点
# 前端创建/编辑模板时，先选择学科/年级/学期/教材版本，然后动态加载对应的知识点选项
# 教材版本使用 ID: rjb=人教版，rjb_2024=人教版（2024 新版），bsd=北师大版，hj=沪教版，等
KNOWLEDGE_POINTS: Dict[str, Dict[str, Dict[str, Dict[str, List[str]]]]] = {
    "math": {
        "grade1": {
            "upper": {
                "rjb_2024": [  # 人教版（2024 新版）
                    "5 以内数的认识和加、减法",
                    "6~10 的认识和加、减法",
                    "11~20 各数的认识",
                    "20 以内的进位加法",
                ],
                "bsd": [  # 北师大版
                    "生活中的数",
                    "比较",
                    "加与减（一）",
                    "加与减（二）",
                ],
            },
            "lower": {
                "rjb_2024": [  # 人教版（2024 新版）
                    "20 以内的退位减法",
                    "100 以内数的认识",
                    "100 以内的口算加、减法",
                    "100 以内的笔算加、减法",
                    "期末复习",
                    "专项练习",
                ],
            },
        },
        "grade2": {
            "upper": {
                "rjb": [  # 人教版
                    "100 以内的加法和减法（二）",
                    "角的初步认识",
                    "表内乘法（一）",
                    "表内乘法（二）",
                ],
            },
            "lower": {
                "rjb": [  # 人教版
                    "数据收集整理",
                    "表内除法（一）",
                    "图形的运动（一）",
                    "表内除法（二）",
                ],
            },
        },
        "grade3": {
            "upper": {
                "rjb": [  # 人教版
                    "时分秒",
                    "万以内的加法和减法（一）",
                    "测量",
                    "倍的认识",
                    "多位数乘一位数",
                ],
            },
            "lower": {
                "rjb": [  # 人教版
                    "位置与方向（一）",
                    "除数是一位数的除法",
                    "两位数乘两位数",
                    "面积",
                ],
            },
        },
    },
    "chinese": {
        "grade1": {
            "upper": {
                "rjb": [  # 人教版
                    "汉语拼音",
                    "识字",
                    "课文阅读",
                    "口语交际",
                ],
            },
            "lower": {
                "rjb": [  # 人教版
                    "识字",
                    "课文阅读",
                    "写话",
                    "语文园地",
                ],
            },
        },
    },
    "english": {
        "grade3": {
            "upper": {
                "rjb": [  # 人教版
                    "字母与发音",
                    "问候与介绍",
                    "数字与颜色",
                    "家庭成员",
                ],
            },
        },
    },
}
