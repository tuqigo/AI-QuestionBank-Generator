"""
模板：乘除综合 - 小学全阶段通用乘除法生成器

设计原则：
- 生成器本身不限制年级，所有范围通过 configuration 控制
- 题型复杂度通过 question_complexity 配置动态选择
- 规则约束通过 rules 配置动态启用
- 后期添加新模板只需 SQL，无需改代码

支持题型：
- 简单乘法/除法
- 乘法/除法填空
- 乘加/乘减/除加/除减混合
- 带余数除法
- 连乘
- 大小比较
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MultiplicationDivisionComprehensiveGenerator(TemplateGenerator):
    """
    乘除综合统一生成器 - 支持小学全阶段

    配置示例（二年级）:
    {
        "factor": {"min": 1, "max": 9},
        "divisor": {"min": 1, "max": 9},
        "dividend": {"min": 1, "max": 81},
        "extra": {"min": 1, "max": 20},
        "question_complexity": ["simple_multiply", "simple_divide"],
        "rules": ["ensure_divisible", "result_within_100"]
    }
    """

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # ==================== 基础配置读取 ====================
        # 因子范围（用于乘法）- 默认 1-9（表内乘法）
        factor_min = template_config.get("factor", {}).get("min", 1)
        factor_max = template_config.get("factor", {}).get("max", 9)

        # 是否固定第一个因子（用于乘法口诀专项练习，如固定为 7）
        fixed_first_factor = template_config.get("fixed_first_factor", None)

        # 除数范围（用于除法）- 默认 1-9
        divisor_min = template_config.get("divisor", {}).get("min", 1)
        divisor_max = template_config.get("divisor", {}).get("max", 9)

        # 被除数范围（用于除法）- 默认 1-81（9×9）
        dividend_min = template_config.get("dividend", {}).get("min", 1)
        dividend_max = template_config.get("dividend", {}).get("max", 81)

        # 商的范围（用于除法）- 默认 1-9
        quotient_min = template_config.get("quotient", {}).get("min", 1)
        quotient_max = template_config.get("quotient", {}).get("max", 9)

        # 额外加/减数的范围（用于混合运算）- 默认 1-20
        extra_min = template_config.get("extra", {}).get("min", 1)
        extra_max = template_config.get("extra", {}).get("max", 20)

        # 连乘因子数量 - 默认 3 个
        chain_factors = template_config.get("chain_factors", 3)

        # 比较题的偏移范围 - 默认 1-10
        compare_offset_min = template_config.get("compare_offset", {}).get("min", 1)
        compare_offset_max = template_config.get("compare_offset", {}).get("max", 10)

        # ==================== 题型复杂度配置 ====================
        # 支持：simple_multiply, simple_divide, multiply_fill_*, divide_fill_*,
        #      multiply_add, multiply_subtract, divide_add, divide_subtract,
        #      remainder_division, compare_multiply, compare_division,
        #      multiply_chain, mixed_compare, multiply_multi_fill, etc.
        question_complexity = template_config.get(
            "question_complexity",
            ["simple_multiply", "simple_divide"]
        )

        # ==================== 规则读取 ====================
        rules = template_config.get("rules", [])
        ensure_divisible = "ensure_divisible" in rules or "ensure_no_remainder" in rules
        ensure_positive = "ensure_positive" in rules
        ensure_remainder = "ensure_remainder" in rules
        ensure_different = "ensure_different" in rules
        ensure_borrowing = "ensure_borrowing" in rules  # 减法需要借位
        ensure_carrying = "ensure_carrying" in rules    # 加法需要进位
        result_within_10 = "result_within_10" in rules
        result_within_20 = "result_within_20" in rules
        result_within_100 = "result_within_100" in rules
        result_within_1000 = "result_within_1000" in rules
        result_limit = template_config.get("result_within", None)  # 自定义结果上限

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                # 随机选择题型
                q_type = random.choice(question_complexity)
                stem = ""
                valid = True

                # ==================== 乘法题型 ====================
                if q_type == "simple_multiply":
                    # 简单乘法：3 × 4 = （ ）
                    if fixed_first_factor is not None:
                        a = fixed_first_factor
                        b = random.randint(factor_min, factor_max)
                    else:
                        a = random.randint(factor_min, factor_max)
                        b = random.randint(factor_min, factor_max)

                    if ensure_different and a == b:
                        continue

                    result = a * b
                    if not self._check_result_limit(result, result_limit, result_within_10, result_within_20, result_within_100, result_within_1000):
                        continue

                    stem = f"${a} \\times {b} = （    ）$"

                elif q_type == "multiply_fill_first":
                    # 乘法填空（求第一个因子）：（ ）× 4 = 12
                    b = random.randint(factor_min, factor_max)
                    result = random.randint(factor_min, factor_max) * b

                    if result > dividend_max:
                        continue

                    stem = f"$（    ） \\times {b} = {result}$"

                elif q_type == "multiply_fill_second":
                    # 乘法填空（求第二个因子）：3 × （ ） = 12
                    a = random.randint(factor_min, factor_max)
                    result = a * random.randint(factor_min, factor_max)

                    if result > dividend_max:
                        continue

                    stem = f"${a} \\times （    ） = {result}$"

                elif q_type == "multiply_fill_both":
                    # 乘法填空（两个因子都未知，较难）：（ ）×（ ） = 12（多解）
                    # 实际只填一个空，但题目设计为开放性
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    result = a * b
                    # 给出一个因子，求另一个
                    if random.choice([True, False]):
                        stem = f"${a} \\times （    ） = {result}$"
                    else:
                        stem = f"$（    ） \\times {b} = {result}$"

                elif q_type == "multiply_add":
                    # 乘加混合：3 × 4 + 5 = （ ）
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    extra = random.randint(extra_min, extra_max)

                    if ensure_carrying and extra == 0:
                        continue

                    result = a * b + extra
                    if not self._check_result_limit(result, result_limit, result_within_10, result_within_20, result_within_100, result_within_1000):
                        continue

                    stem = f"${a} \\times {b} + {extra} = （    ）$"

                elif q_type == "multiply_subtract":
                    # 乘减混合：3 × 4 - 5 = （ ）
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    extra = random.randint(extra_min, max(extra_min, a * b - 1))

                    result = a * b - extra
                    if ensure_positive and result < 0:
                        continue
                    if not self._check_result_limit(result, result_limit, result_within_10, result_within_20, result_within_100, result_within_1000):
                        continue

                    stem = f"${a} \\times {b} - {extra} = （    ）$"

                elif q_type == "multiply_chain":
                    # 连乘：2 × 3 × 4 = （ ）
                    num_factors = min(chain_factors, 5)  # 最多 5 个因子
                    factors = []
                    for i in range(num_factors):
                        if i == 0:
                            factors.append(random.randint(factor_min, factor_max))
                        else:
                            factors.append(random.randint(2, min(factor_max, 9)))

                    result = 1
                    for f in factors:
                        result *= f

                    if not self._check_result_limit(result, result_limit, result_within_10, result_within_20, result_within_100, result_within_1000):
                        continue

                    stem = " \\times ".join(map(str, factors)) + " = （    ）"
                    stem = f"${stem}$"

                # ==================== 除法题型 ====================
                elif q_type == "simple_divide":
                    # 简单除法：12 ÷ 3 = （ ）
                    # 先生成商和除数，再计算被除数，确保整除
                    quotient = random.randint(quotient_min, quotient_max)
                    divisor = random.randint(divisor_min, divisor_max)

                    if ensure_different and quotient == divisor:
                        continue

                    dividend = quotient * divisor
                    if dividend > dividend_max or dividend < dividend_min:
                        continue

                    stem = f"${dividend} \\div {divisor} = （    ）$"

                elif q_type == "divide_fill_dividend":
                    # 除法填空（求被除数）：（ ）÷ 3 = 4
                    divisor = random.randint(divisor_min, divisor_max)
                    quotient = random.randint(quotient_min, quotient_max)
                    dividend = divisor * quotient

                    if dividend > dividend_max:
                        continue

                    stem = f"$（    ） \\div {divisor} = {quotient}$"

                elif q_type == "divide_fill_divisor":
                    # 除法填空（求除数）：12 ÷ （ ） = 4
                    quotient = random.randint(quotient_min, quotient_max)
                    divisor = random.randint(divisor_min, divisor_max)
                    dividend = quotient * divisor

                    if dividend > dividend_max:
                        continue

                    stem = f"${dividend} \\div （    ） = {quotient}$"

                elif q_type == "divide_fill_quotient_remainder":
                    # 带余数除法填空：（ ）÷ 3 = 4 …… 2
                    divisor = random.randint(divisor_min, divisor_max)
                    quotient = random.randint(quotient_min, quotient_max)
                    if ensure_remainder:
                        remainder = random.randint(1, divisor - 1)
                    else:
                        remainder = random.randint(0, divisor - 1)

                    dividend = quotient * divisor + remainder
                    if dividend > dividend_max:
                        continue

                    stem = f"$（    ） \\div {divisor} = {quotient} \\dots \\dots （    ）$"

                elif q_type == "divide_add":
                    # 除加混合：12 ÷ 3 + 5 = （ ）
                    quotient = random.randint(quotient_min, quotient_max)
                    divisor = random.randint(divisor_min, divisor_max)
                    extra = random.randint(extra_min, extra_max)

                    dividend = quotient * divisor
                    if dividend > dividend_max:
                        continue

                    result = quotient + extra
                    if not self._check_result_limit(result, result_limit, result_within_10, result_within_20, result_within_100, result_within_1000):
                        continue

                    stem = f"${dividend} \\div {divisor} + {extra} = （    ）$"

                elif q_type == "divide_subtract":
                    # 除减混合：12 ÷ 3 - 2 = （ ）
                    quotient = random.randint(max(2, quotient_min), quotient_max)
                    divisor = random.randint(divisor_min, divisor_max)
                    extra = random.randint(extra_min, min(extra_max, quotient - 1))

                    dividend = quotient * divisor
                    if dividend > dividend_max:
                        continue

                    result = quotient - extra
                    if ensure_positive and result < 0:
                        continue

                    stem = f"${dividend} \\div {divisor} - {extra} = （    ）$"

                elif q_type == "remainder_division":
                    # 带余数除法：11 ÷ 2 = （ ）  学生填写 5……1
                    # 注意：余数必须大于 0 且小于除数
                    divisor = random.randint(divisor_min, divisor_max)
                    quotient = random.randint(quotient_min, quotient_max)
                    remainder = random.randint(1, divisor - 1)

                    dividend = quotient * divisor + remainder
                    if dividend > dividend_max:
                        continue

                    stem = f"${dividend} \\div {divisor} = （    ）$"

                # ==================== 比较题型 ====================
                elif q_type == "compare_multiply":
                    # 乘法比较：3 × 4 （ ） 10
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    result = a * b

                    compare_type = random.choice(["equal", "greater", "less"])
                    offset = random.randint(compare_offset_min, compare_offset_max)
                    if compare_type == "equal":
                        compare_num = result
                    elif compare_type == "greater":
                        compare_num = result + offset
                    else:
                        compare_num = result - offset
                        if compare_num < 0:
                            compare_num = result + offset

                    stem = f"${a} \\times {b} （    ） {compare_num}$"

                elif q_type == "compare_division":
                    # 除法比较：12 ÷ 3 （ ） 4
                    quotient = random.randint(quotient_min, quotient_max)
                    divisor = random.randint(divisor_min, divisor_max)
                    dividend = quotient * divisor

                    if dividend > dividend_max:
                        continue

                    compare_type = random.choice(["equal", "greater", "less"])
                    offset = random.randint(compare_offset_min, min(compare_offset_max, 5))
                    if compare_type == "equal":
                        compare_num = quotient
                    elif compare_type == "greater":
                        compare_num = quotient + offset
                    else:
                        compare_num = quotient - offset
                        if compare_num < 0:
                            compare_num = quotient + offset

                    stem = f"${dividend} \\div {divisor} （    ） {compare_num}$"

                elif q_type == "compare_multiply_division":
                    # 乘除混合比较：3 × 4 （ ） 12 ÷ 2
                    # 乘法侧
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    left_result = a * b

                    # 除法侧
                    q_right = random.randint(quotient_min, quotient_max)
                    d_right = random.randint(divisor_min, divisor_max)
                    right_result = q_right * d_right

                    if right_result > dividend_max:
                        continue

                    # 决定大小关系
                    compare_type = random.choice(["equal", "greater", "less"])
                    if compare_type == "equal":
                        right_result = left_result
                    elif compare_type == "greater":
                        if right_result <= left_result:
                            right_result = left_result + random.randint(1, 10)
                    else:
                        if right_result >= left_result:
                            right_result = max(1, left_result - random.randint(1, 10))

                    stem = f"${a} \\times {b} （    ） {right_result}$"

                elif q_type == "mixed_compare":
                    # 混合运算比较：3 × 4 + 2 （ ） 15
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    extra = random.randint(extra_min, extra_max)

                    result = a * b + extra
                    if not self._check_result_limit(result, result_limit, result_within_10, result_within_20, result_within_100, result_within_1000):
                        continue

                    compare_type = random.choice(["equal", "greater", "less"])
                    offset = random.randint(compare_offset_min, compare_offset_max)
                    if compare_type == "equal":
                        compare_num = result
                    elif compare_type == "greater":
                        compare_num = result + offset
                    else:
                        compare_num = result - offset
                        if compare_num < 0:
                            compare_num = result + offset

                    stem = f"${a} \\times {b} + {extra} （    ） {compare_num}$"

                else:
                    # 默认：简单乘法
                    a = random.randint(factor_min, factor_max)
                    b = random.randint(factor_min, factor_max)
                    stem = f"${a} \\times {b} = （    ）$"

                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                # 100 次尝试后仍未生成有效题目，跳过
                continue

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 3,
            })

        return questions

    def _check_result_limit(
        self,
        result: int,
        result_limit: int = None,
        result_within_10: bool = False,
        result_within_20: bool = False,
        result_within_100: bool = False,
        result_within_1000: bool = False
    ) -> bool:
        """检查结果是否符合限制条件"""
        if result_limit is not None and result > result_limit:
            return False
        if result_within_10 and result > 10:
            return False
        if result_within_20 and result > 20:
            return False
        if result_within_100 and result > 100:
            return False
        if result_within_1000 and result > 1000:
            return False
        return True

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        """
        根据配置动态返回知识点
        可通过配置覆盖默认的知识点列表
        """
        # 支持通过配置自定义知识点
        if "knowledge_points" in template_config:
            return template_config["knowledge_points"]

        # 默认知识点（根据题型动态判断）
        question_complexity = template_config.get("question_complexity", [])
        points = []

        if any(t in question_complexity for t in ["simple_multiply", "multiply_fill_first", "multiply_fill_second", "multiply_chain"]):
            points.append("表内乘法")
        if any(t in question_complexity for t in ["simple_divide", "divide_fill_dividend", "divide_fill_divisor"]):
            points.append("表内除法")
        if any(t in question_complexity for t in ["multiply_add", "multiply_subtract", "divide_add", "divide_subtract"]):
            points.append("乘除混合运算")
        if "remainder_division" in question_complexity:
            points.append("带余数除法")
        if any("compare" in t for t in question_complexity):
            points.append("大小比较")

        return points if points else ["乘除法综合练习"]
