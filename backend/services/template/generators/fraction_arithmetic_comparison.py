"""
模板：分数加减乘除比较大小综合生成器

支持题型（小学 3-6 年级）：
- 同分母分数加减法
- 异分母分数加减法（通分）
- 分数乘法（分数×整数、分数×分数）
- 分数除法（分数÷整数、分数÷分数）
- 分数加减乘除混合运算
- 分数比大小（同分母、同分子、异分母）
- 分数与小数比较
- 带分数运算
- 倒数
- 分数乘加、乘减、除加、除减混合
"""
import random
from math import gcd
from typing import List, Dict, Any, Tuple, Optional

from .base import TemplateGenerator


def simplify_fraction(numerator: int, denominator: int) -> Tuple[int, int]:
    """约分分数"""
    if denominator == 0:
        raise ValueError("分母不能为 0")
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    common = gcd(abs(numerator), abs(denominator))
    return numerator // common, denominator // common


def lcm(a: int, b: int) -> int:
    """求最小公倍数"""
    return abs(a * b) // gcd(a, b)


class FractionArithmeticComparisonGenerator(TemplateGenerator):
    """
    分数加减乘除比较大小综合生成器 - 支持小学 3-6 年级

    配置示例（三年级 - 同分母分数加减法）:
    {
        "denominator": {"min": 2, "max": 10},
        "numerator": {"min": 1},
        "question_complexity": ["same_denominator_add", "same_denominator_subtract"],
        "rules": ["ensure_proper_fraction", "result_proper_fraction"]
    }

    配置示例（五年级 - 异分母分数加减法）:
    {
        "denominator": {"min": 2, "max": 20},
        "numerator": {"min": 1},
        "question_complexity": ["different_denominator_add", "different_denominator_subtract"],
        "rules": ["ensure_simplest_result"]
    }

    配置示例（六年级 - 分数乘除混合）:
    {
        "denominator": {"min": 2, "max": 15},
        "numerator": {"min": 1},
        "question_complexity": ["multiply", "divide", "multiply_divide_mixed"],
        "rules": ["ensure_simplest_result", "ensure_proper_fraction"]
    }
    """

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # ==================== 基础配置读取 ====================
        # 分母范围 - 默认 2-10
        denominator_min = template_config.get("denominator", {}).get("min", 2)
        denominator_max = template_config.get("denominator", {}).get("max", 10)

        # 分子范围 - 默认跟随分母
        numerator_min = template_config.get("numerator", {}).get("min", 1)
        numerator_max = template_config.get("numerator", {}).get("max", None)  # None 表示跟随分母

        # 整数部分范围（用于带分数）- 默认 1-5
        whole_min = template_config.get("whole", {}).get("min", 1)
        whole_max = template_config.get("whole", {}).get("max", 5)

        # 比较题偏移范围 - 默认 1-5
        compare_offset_min = template_config.get("compare_offset", {}).get("min", 1)
        compare_offset_max = template_config.get("compare_offset", {}).get("max", 5)

        # ==================== 题型复杂度配置 ====================
        # 支持题型：
        # 加减法：same_denominator_add/subtract, different_denominator_add/subtract, mixed_add_subtract
        # 乘法：multiply_fraction_int, multiply_fraction_fraction, multiply_mixed
        # 除法：divide_fraction_int, divide_fraction_fraction, divide_mixed
        # 混合运算：multiply_add, multiply_subtract, divide_add, divide_subtract, mixed_operations
        # 比较：compare_same_denominator, compare_same_numerator, compare_different, compare_with_decimal
        # 其他：reciprocal, fill_blank_*
        question_complexity = template_config.get(
            "question_complexity",
            ["same_denominator_add", "same_denominator_subtract"]
        )

        # ==================== 规则读取 ====================
        rules = template_config.get("rules", [])
        ensure_proper_fraction = "ensure_proper_fraction" in rules  # 确保是真分数
        ensure_simplest_result = "ensure_simplest_result" in rules  # 确保结果是最简分数
        result_proper_fraction = "result_proper_fraction" in rules  # 确保结果是真分数
        ensure_different_denominator = "ensure_different_denominator" in rules  # 确保分母不同
        ensure_integer_result = "ensure_integer_result" in rules  # 确保结果是整数
        ensure_positive = "ensure_positive" in rules  # 确保结果为正

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        # 支持通过 q_type 设置 answer_style（优先级高于 rendering_config）
        q_type_styles = template_config.get("q_type", {})
        if isinstance(q_type_styles, str):
            q_type_styles = {q_type_styles: "circle"}

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                # 随机选择题型
                q_type = random.choice(question_complexity)
                stem = ""
                valid = True

                # ==================== 同分母分数加减法 ====================
                if q_type == "same_denominator_add":
                    # 同分母分数加法：1/5 + 2/5 = [BLANK]
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)
                    numerator2 = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)

                    result_numerator = numerator1 + numerator2
                    if result_proper_fraction and result_numerator > denominator:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator}}} + \\frac{{{numerator2}}}{{{denominator}}} = [BLANK]$"

                elif q_type == "same_denominator_subtract":
                    # 同分母分数减法：3/5 - 1/5 = [BLANK]
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min + 1, denominator)
                    numerator2 = random.randint(numerator_min, numerator1 - 1)

                    if ensure_proper_fraction and numerator1 >= denominator:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator}}} - \\frac{{{numerator2}}}{{{denominator}}} = [BLANK]$"

                # ==================== 异分母分数加减法 ====================
                elif q_type == "different_denominator_add":
                    # 异分母分数加法：1/3 + 1/4 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)

                    if ensure_different_denominator and denominator1 == denominator2:
                        continue

                    numerator1 = random.randint(numerator_min, denominator1 - 1 if ensure_proper_fraction else denominator1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1 if ensure_proper_fraction else denominator2)

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} + \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "different_denominator_subtract":
                    # 异分母分数减法：3/4 - 1/3 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)

                    if ensure_different_denominator and denominator1 == denominator2:
                        continue

                    numerator1 = random.randint(numerator_min + 1, denominator1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1)

                    # 确保结果为正（交叉相乘比较）
                    if numerator1 * denominator2 <= numerator2 * denominator1:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} - \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                # ==================== 分数乘法 ====================
                elif q_type == "multiply_fraction_int":
                    # 分数乘整数：2/3 × 4 = [BLANK]
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator if ensure_proper_fraction else denominator * 2)
                    multiplier = random.randint(2, 9)

                    stem = f"$\\frac{{{numerator}}}{{{denominator}}} \\times {multiplier} = [BLANK]$"

                elif q_type == "multiply_fraction_fraction":
                    # 分数乘分数：1/2 × 2/3 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 if ensure_proper_fraction else denominator1)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 if ensure_proper_fraction else denominator2)

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\times \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "multiply_mixed":
                    # 带分数乘法：1 1/2 × 2/3 = [BLANK]
                    whole = random.randint(whole_min, whole_max)
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator - 1)
                    multiplier_num = random.randint(2, 5)
                    multiplier_den = random.randint(2, 5)

                    stem = f"${whole}\\frac{{{numerator}}}{{{denominator}}} \\times \\frac{{{multiplier_num}}}{{{multiplier_den}}} = [BLANK]$"

                # ==================== 分数除法 ====================
                elif q_type == "divide_fraction_int":
                    # 分数除整数：3/4 ÷ 2 = [BLANK]
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator if ensure_proper_fraction else denominator)
                    divisor = random.randint(2, 9)

                    stem = f"$\\frac{{{numerator}}}{{{denominator}}} \\div {divisor} = [BLANK]$"

                elif q_type == "divide_fraction_fraction":
                    # 分数除分数：1/2 ÷ 1/4 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 if ensure_proper_fraction else denominator1)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 if ensure_proper_fraction else denominator2)

                    if numerator2 == 0:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\div \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "divide_mixed":
                    # 带分数除法：1 1/2 ÷ 1/2 = [BLANK]
                    whole = random.randint(whole_min, whole_max)
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator - 1)
                    divisor_num = random.randint(1, 3)
                    divisor_den = random.randint(2, 5)

                    stem = f"${whole}\\frac{{{numerator}}}{{{denominator}}} \\div \\frac{{{divisor_num}}}{{{divisor_den}}} = [BLANK]$"

                # ==================== 分数加减混合 ====================
                elif q_type == "mixed_add_subtract":
                    # 分数加减混合：1/2 + 1/3 - 1/6 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    denominator3 = random.randint(denominator_min, denominator_max)

                    numerator1 = random.randint(numerator_min, denominator1 - 1 if ensure_proper_fraction else denominator1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1 if ensure_proper_fraction else denominator2)
                    numerator3 = random.randint(numerator_min, denominator3 - 1 if ensure_proper_fraction else denominator3)

                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} {op1} \\frac{{{numerator2}}}{{{denominator2}}} {op2} \\frac{{{numerator3}}}{{{denominator3}}} = [BLANK]$"

                # ==================== 分数乘除混合 ====================
                elif q_type == "multiply_divide_mixed":
                    # 分数乘除混合：1/2 × 3/4 ÷ 1/8 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 if ensure_proper_fraction else denominator1)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 if ensure_proper_fraction else denominator2)
                    denominator3 = random.randint(denominator_min, denominator_max)
                    numerator3 = random.randint(1, denominator3 if ensure_proper_fraction else denominator3)

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\times \\frac{{{numerator2}}}{{{denominator2}}} \\div \\frac{{{numerator3}}}{{{denominator3}}} = [BLANK]$"

                # ==================== 分数乘加/乘减混合 ====================
                elif q_type == "multiply_add":
                    # 分数乘加：1/2 × 3 + 1/4 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 if ensure_proper_fraction else denominator1)
                    multiplier = random.randint(2, 9)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 - 1 if ensure_proper_fraction else denominator2)

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\times {multiplier} + \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "multiply_subtract":
                    # 分数乘减：3/4 × 2 - 1/2 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 if ensure_proper_fraction else denominator1)
                    multiplier = random.randint(2, 5)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 - 1)

                    # 确保结果为正
                    result_num = numerator1 * multiplier * denominator2 - numerator2 * denominator1
                    if result_num <= 0:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\times {multiplier} - \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "divide_add":
                    # 分数除加：3/4 ÷ 2 + 1/8 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 if ensure_proper_fraction else denominator1)
                    divisor = random.randint(2, 5)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 - 1 if ensure_proper_fraction else denominator2)

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\div {divisor} + \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "divide_subtract":
                    # 分数除减：3/4 ÷ 2 - 1/8 = [BLANK]
                    denominator1 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min + 1, denominator1)
                    divisor = random.randint(2, 5)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator2 - 1)

                    # 确保结果为正
                    result_num = numerator1 * denominator2 - numerator2 * denominator1 * divisor
                    if result_num <= 0:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} \\div {divisor} - \\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                # ==================== 分数比大小 ====================
                elif q_type == "compare_same_denominator":
                    # 同分母分数比较：2/5 [BLANK] 3/5
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)
                    numerator2 = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)

                    if ensure_different_denominator and numerator1 == numerator2:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator}}}$ [BLANK] $\\frac{{{numerator2}}}{{{denominator}}}$"

                elif q_type == "compare_same_numerator":
                    # 同分子分数比较：2/3 [BLANK] 2/5
                    numerator = random.randint(numerator_min, min(denominator_min, denominator_max))
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)

                    if ensure_different_denominator and denominator1 == denominator2:
                        continue
                    if ensure_proper_fraction and (numerator >= denominator1 or numerator >= denominator2):
                        continue

                    stem = f"$\\frac{{{numerator}}}{{{denominator1}}}$ [BLANK] $\\frac{{{numerator}}}{{{denominator2}}}$"

                elif q_type == "compare_different":
                    # 异分母分数比较：3/4 [BLANK] 2/3
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)

                    if ensure_different_denominator and denominator1 == denominator2:
                        continue

                    numerator1 = random.randint(numerator_min, denominator1 - 1 if ensure_proper_fraction else denominator1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1 if ensure_proper_fraction else denominator2)

                    # 避免相等的情况
                    if numerator1 * denominator2 == numerator2 * denominator1:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}}$ [BLANK] $\\frac{{{numerator2}}}{{{denominator2}}}$"

                elif q_type == "compare_with_result":
                    # 运算后比较：1/2 + 1/3 [BLANK] 5/6
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 - 1 if ensure_proper_fraction else denominator1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1 if ensure_proper_fraction else denominator2)

                    op = random.choice(["+", "-"])
                    if op == "-" and numerator1 * denominator2 <= numerator2 * denominator1:
                        continue

                    # 计算结果
                    if op == "+":
                        result_num = numerator1 * denominator2 + numerator2 * denominator1
                    else:
                        result_num = numerator1 * denominator2 - numerator2 * denominator1
                    result_den = denominator1 * denominator2

                    # 生成比较数
                    compare_type = random.choice(["equal", "greater", "less"])
                    offset = random.randint(compare_offset_min, compare_offset_max)
                    if compare_type == "equal":
                        compare_num = result_num
                        compare_den = result_den
                    elif compare_type == "greater":
                        compare_num = result_num + offset * result_den
                        compare_den = result_den
                    else:
                        compare_num = max(1, result_num - offset * result_den)
                        compare_den = result_den

                    if compare_num <= 0:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}} {op} \\frac{{{numerator2}}}{{{denominator2}}}$ [BLANK] $\\frac{{{compare_num}}}{{{compare_den}}}$"

                elif q_type == "compare_multiply":
                    # 乘法结果比较：1/2 × 3 [BLANK] 2
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator if ensure_proper_fraction else denominator)
                    multiplier = random.randint(2, 5)

                    result_num = numerator * multiplier
                    compare_type = random.choice(["equal", "greater", "less"])
                    offset = random.randint(1, 3)

                    if compare_type == "equal":
                        compare = f"$\\frac{{{result_num}}}{{{denominator}}}$"
                    elif compare_type == "greater":
                        compare_num = result_num + offset * denominator
                        compare = f"$\\frac{{{compare_num}}}{{{denominator}}}$"
                    else:
                        compare_num = max(1, result_num - offset * denominator)
                        compare = f"$\\frac{{{compare_num}}}{{{denominator}}}$"

                    stem = f"$\\frac{{{numerator}}}{{{denominator}}} \\times {multiplier}$ [BLANK] {compare}"

                elif q_type == "compare_divide":
                    # 除法结果比较：3/4 ÷ 2 [BLANK] 1/2
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator if ensure_proper_fraction else denominator)
                    divisor = random.randint(2, 5)

                    result_num = numerator
                    result_den = denominator * divisor

                    compare_type = random.choice(["equal", "greater", "less"])
                    offset = random.randint(1, 3)

                    if compare_type == "equal":
                        compare = f"$\\frac{{{result_num}}}{{{result_den}}}$"
                    elif compare_type == "greater":
                        compare_num = result_num + offset * result_den
                        compare = f"$\\frac{{{compare_num}}}{{{result_den}}}$"
                    else:
                        compare_num = max(1, result_num - offset * result_den)
                        compare = f"$\\frac{{{compare_num}}}{{{result_den}}}$"

                    stem = f"$\\frac{{{numerator}}}{{{denominator}}} \\div {divisor}$ [BLANK] {compare}"

                # ==================== 填空题 ====================
                elif q_type == "fill_blank_numerator":
                    # 填分子：[BLANK]/5 + 2/5 = 4/5
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator2 = random.randint(numerator_min, denominator - 1)
                    result_num = random.randint(numerator2 + 1, denominator)
                    numerator1 = result_num - numerator2

                    if numerator1 <= 0:
                        continue

                    stem = f"$\\frac{{[BLANK]}}{{{denominator}}} + \\frac{{{numerator2}}}{{{denominator}}} = \\frac{{{result_num}}}{{{denominator}}}$"

                elif q_type == "fill_blank_denominator":
                    # 填分母：1/[BLANK] + 1/5 = 2/5
                    numerator = random.randint(numerator_min, 3)
                    denominator2 = random.randint(denominator_min + 1, denominator_max)
                    result_num = numerator * 2
                    result_den = denominator2

                    stem = f"$\\frac{{{numerator}}}{{[BLANK]}} + \\frac{{{numerator}}}{{{denominator2}}} = \\frac{{{result_num}}}{{{result_den}}}$"

                elif q_type == "fill_blank_operation":
                    # 填运算符：1/2 [BLANK] 1/3 = 5/6
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(1, denominator1 - 1)
                    numerator2 = random.randint(1, denominator2 - 1)

                    # 随机选择加法或减法
                    if random.choice([True, False]):
                        result_num = numerator1 * denominator2 + numerator2 * denominator1
                        op = "+"
                    else:
                        if numerator1 * denominator2 <= numerator2 * denominator1:
                            continue
                        result_num = numerator1 * denominator2 - numerator2 * denominator1
                        op = "-"
                    result_den = denominator1 * denominator2

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}}$ [BLANK] $\\frac{{{numerator2}}}{{{denominator2}}} = \\frac{{{result_num}}}{{{result_den}}}$"

                # ==================== 倒数 ====================
                elif q_type == "reciprocal":
                    # 求倒数：3/4 的倒数是 [BLANK]
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)

                    stem = f"$\\frac{{{numerator}}}{{{denominator}}}$ 的倒数是 [BLANK]"

                # ==================== 带分数 ====================
                elif q_type == "mixed_number_add":
                    # 带分数加法：1 1/2 + 2 1/3 = [BLANK]
                    whole1 = random.randint(whole_min, whole_max)
                    whole2 = random.randint(whole_min, whole_max)
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 - 1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1)

                    stem = f"${whole1}\\frac{{{numerator1}}}{{{denominator1}}} + {whole2}\\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                elif q_type == "mixed_number_subtract":
                    # 带分数减法：3 3/4 - 1 1/2 = [BLANK]
                    whole1 = random.randint(whole_min + 1, whole_max + 2)
                    whole2 = random.randint(whole_min, whole1 - 1)
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator1 - 1)
                    numerator2 = random.randint(numerator_min, denominator2 - 1)

                    stem = f"${whole1}\\frac{{{numerator1}}}{{{denominator1}}} - {whole2}\\frac{{{numerator2}}}{{{denominator2}}} = [BLANK]$"

                else:
                    # 默认：同分母分数加法
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator - 1)
                    numerator2 = random.randint(numerator_min, denominator - 1)
                    stem = f"$\\frac{{{numerator1}}}{{{denominator}}} + \\frac{{{numerator2}}}{{{denominator}}} = [BLANK]$"

                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                # 100 次尝试后仍未生成有效题目，跳过
                continue

            # 应用 q_type 级别的 answer_style 配置
            question_rendering_meta = rendering_meta.copy()
            if q_type in q_type_styles:
                question_rendering_meta["answer_style"] = q_type_styles[q_type]

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config, q_type),
                "rows_to_answer": 3,
                "rendering_meta": question_rendering_meta,
            })

        return questions

    def get_knowledge_points(self, template_config: dict, q_type: str = None) -> List[str]:
        """
        根据配置和题型动态返回知识点
        """
        # 支持通过配置自定义知识点
        if "knowledge_points" in template_config:
            return template_config["knowledge_points"]

        # 根据题型返回对应的知识点
        knowledge_map = {
            # 同分母加减法
            "same_denominator_add": ["同分母分数加法", "分数加法基础"],
            "same_denominator_subtract": ["同分母分数减法", "分数减法基础"],
            # 异分母加减法
            "different_denominator_add": ["异分母分数加法", "通分", "最小公倍数"],
            "different_denominator_subtract": ["异分母分数减法", "通分", "最小公倍数"],
            # 混合加减
            "mixed_add_subtract": ["分数加减混合运算", "通分"],
            # 乘法
            "multiply_fraction_int": ["分数乘整数", "分数乘法基础"],
            "multiply_fraction_fraction": ["分数乘分数", "分数乘法"],
            "multiply_mixed": ["带分数乘法", "分数乘法"],
            # 除法
            "divide_fraction_int": ["分数除整数", "分数除法基础"],
            "divide_fraction_fraction": ["分数除分数", "倒数", "分数除法"],
            "divide_mixed": ["带分数除法", "分数除法"],
            # 乘除混合
            "multiply_divide_mixed": ["分数乘除混合运算", "倒数"],
            # 乘加/乘减混合
            "multiply_add": ["分数乘加混合运算", "运算顺序"],
            "multiply_subtract": ["分数乘减混合运算", "运算顺序"],
            "divide_add": ["分数除加混合运算", "运算顺序"],
            "divide_subtract": ["分数除减混合运算", "运算顺序"],
            # 比较
            "compare_same_denominator": ["同分母分数比较大小"],
            "compare_same_numerator": ["同分子分数比较大小"],
            "compare_different": ["异分母分数比较大小", "通分"],
            "compare_with_result": ["分数运算比较", "综合应用"],
            "compare_multiply": ["乘法结果比较"],
            "compare_divide": ["除法结果比较"],
            # 填空
            "fill_blank_numerator": ["填分子", "逆向思维"],
            "fill_blank_denominator": ["填分母", "逆向思维"],
            "fill_blank_operation": ["填运算符", "逆向思维"],
            # 倒数
            "reciprocal": ["倒数的认识"],
            # 带分数
            "mixed_number_add": ["带分数加法", "假分数"],
            "mixed_number_subtract": ["带分数减法", "假分数"],
        }

        if q_type and q_type in knowledge_map:
            return knowledge_map[q_type]

        return ["分数综合练习"]
