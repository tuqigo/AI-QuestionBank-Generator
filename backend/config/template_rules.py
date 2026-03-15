"""
模板生成规则配置

规则按功能分类，便于生成器按需使用。
未来可以通过数据库表 `generator_rules` 管理，实现动态扩展。
"""

# ===================== 数值范围约束 =====================
RESULT_WITHIN_RULES = {
    "result_within_10": "确保结果 ≤ 10（一年级）",
    "result_within_20": "确保结果 ≤ 20（二年级）",
    "result_within_100": "确保结果 ≤ 100（三年级）",
    "result_within_1000": "确保结果 ≤ 1000（四年级）",
}

# ===================== 数值属性约束 =====================
NUMERIC_PROPERTY_RULES = {
    "ensure_different": "确保两个数不同（用于比大小）",
    "ensure_positive": "确保减法结果不为负数",
    "ensure_non_zero": "确保不为零（用于除法、分母）",
    "ensure_even": "确保是偶数",
    "ensure_odd": "确保是奇数",
    "ensure_prime": "确保是质数",
    "ensure_coprime": "确保互质（用于分数约分）",
}

# ===================== 运算约束 =====================
OPERATION_RULES = {
    "ensure_divisible": "确保除法能整除",
    "ensure_no_remainder": "确保除法无余数",
    "ensure_borrowing": "确保减法需要借位",
    "ensure_carrying": "确保加法需要进位",
}

# ===================== 分数相关约束 =====================
FRACTION_RULES = {
    "ensure_proper_fraction": "确保是真分数（分子 < 分母）",
    "ensure_simplest_form": "确保是最简分数",
    "ensure_common_denominator": "确保同分母",
}

# ===================== 几何/单位约束 =====================
GEOMETRY_RULES = {
    "ensure_realistic_value": "确保是实际存在的值（如长度为正）",
    "ensure_integer_result": "确保计算结果为整数",
}

# ===================== 去重约束 =====================
UNIQUENESS_RULES = {
    "ensure_unique_stem": "确保题干不重复（默认开启）",
}

# ===================== 完整规则字典 =====================
# 合并所有规则，用于全局验证
SUPPORTED_RULES = {
    **RESULT_WITHIN_RULES,
    **NUMERIC_PROPERTY_RULES,
    **OPERATION_RULES,
    **FRACTION_RULES,
    **GEOMETRY_RULES,
    **UNIQUENESS_RULES,
}

# ===================== 年级到规则的快捷映射 =====================
# 便于前端按年级过滤可用的规则
GRADE_RULES_MAP = {
    "grade1": list(RESULT_WITHIN_RULES.keys())[:1] + list(NUMERIC_PROPERTY_RULES.keys())[:3],
    "grade2": list(RESULT_WITHIN_RULES.keys())[:2] + list(NUMERIC_PROPERTY_RULES.keys())[:3],
    "grade3": list(RESULT_WITHIN_RULES.keys())[:3] + list(NUMERIC_PROPERTY_RULES.keys())[:3] + list(OPERATION_RULES.keys())[:2],
}
