"""
模板：小数乘除法综合生成器

支持题型（小学 3-6 年级）：
- 小数乘整数
- 小数乘小数
- 整数乘法运算定律推广到小数（交换律、结合律、分配律）
- 小数除以整数
- 一个数除以小数
- 小数乘除混合运算
- 商的近似值（四舍五入、进一法、去尾法）
- 循环小数
- 小数乘除比较大小
- 小数乘除填空

参考人教版小学数学教材:
- 三年级下册：小数的初步认识
- 四年级下册：小数的意义和性质、小数的加减法
- 五年级上册：小数乘法、小数除法
- 六年级上册：小数乘除综合应用
"""
import random
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING, ROUND_FLOOR
from typing import List, Dict, Any, Tuple, Optional

from .base import TemplateGenerator


def round_decimal(value: float, places: int, method: str = "half_up") -> float:
    """按指定方法保留小数位数"""
    d = Decimal(str(value))
    quantize_str = "0." + "0" * places if places > 0 else "0"

    if method == "half_up":
        result = d.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
    elif method == "ceiling":
        result = d.quantize(Decimal(quantize_str), rounding=ROUND_CEILING)
    elif method == "floor":
        result = d.quantize(Decimal(quantize_str), rounding=ROUND_FLOOR)
    else:
        result = d.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

    return float(result)


def format_decimal(value: float) -> str:
    """格式化小数，去除末尾的 0"""
    if value == int(value):
        return str(int(value))
    return str(value).rstrip('0').rstrip('.')


class DecimalArithmeticGenerator(TemplateGenerator):
    """
    小数乘除法综合生成器 - 支持小学 3-6 年级

    配置示例（五年级 - 小数乘整数）:
    {
        "decimal_places": {"min": 1, "max": 2},
        "factor_int": {"min": 2, "max": 10},
        "question_complexity": ["multiply_decimal_int"],
        "rules": ["result_two_decimal_places"]
    }

    配置示例（五年级 - 小数乘小数）:
    {
        "decimal_places_factor1": {"min": 1, "max": 2},
        "decimal_places_factor2": {"min": 1, "max": 1},
        "question_complexity": ["multiply_decimal_decimal"],
        "rules": ["result_two_decimal_places"]
    }

    配置示例（五年级 - 商的近似值）:
    {
        "dividend_range": {"min": 1, "max": 100},
        "divisor_range": {"min": 2, "max": 20},
        "question_complexity": ["approximate_quotient"],
        "approximate_places": 2,
        "approximate_method": "half_up"
    }
    """

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # ==================== 基础配置读取 ====================
        # 小数位数配置
        decimal_places_min = template_config.get("decimal_places", {}).get("min", 1)
        decimal_places_max = template_config.get("decimal_places", {}).get("max", 2)

        # 因数 1 的小数位数（用于小数乘小数）
        decimal_places_factor1 = template_config.get("decimal_places_factor1", {}).get("min", 1)
        decimal_places_factor1_max = template_config.get("decimal_places_factor1", {}).get("max", decimal_places_factor1)

        # 因数 2 的小数位数（用于小数乘小数）
        decimal_places_factor2 = template_config.get("decimal_places_factor2", {}).get("min", 1)
        decimal_places_factor2_max = template_config.get("decimal_places_factor2", {}).get("max", decimal_places_factor2)

        # 整数因数范围（用于小数乘整数）
        factor_int_min = template_config.get("factor_int", {}).get("min", 2)
        factor_int_max = template_config.get("factor_int", {}).get("max", 10)

        # 小数因数范围
        decimal_factor_min = template_config.get("decimal_factor", {}).get("min", 0.1)
        decimal_factor_max = template_config.get("decimal_factor", {}).get("max", 9.9)

        # 被除数范围
        dividend_min = template_config.get("dividend_range", {}).get("min", 1)
        dividend_max = template_config.get("dividend_range", {}).get("max", 100)

        # 除数范围
        divisor_min = template_config.get("divisor_range", {}).get("min", 2)
        divisor_max = template_config.get("divisor_range", {}).get("max", 20)

        # 商的近似值保留位数
        approximate_places = template_config.get("approximate_places", 2)
        approximate_method = template_config.get("approximate_method", "half_up")

        # 循环小数循环节长度
        repeating_length = template_config.get("repeating_length", 2)

        # ==================== 题型复杂度配置 ====================
        question_complexity = template_config.get(
            "question_complexity",
            ["multiply_decimal_int"]
        )

        # ==================== 规则读取 ====================
        rules = template_config.get("rules", [])
        result_one_decimal_places = "result_one_decimal_places" in rules
        result_two_decimal_places = "result_two_decimal_places" in rules
        result_integer = "result_integer" in rules
        ensure_simple_calculation = "ensure_simple_calculation" in rules  # 确保计算简单
        no_remainder = "no_remainder" in rules  # 除法无余数

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        # 支持通过 q_type 设置 answer_style
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

                # ==================== 小数乘整数 ====================
                if q_type == "multiply_decimal_int":
                    # 小数乘整数：0.5 × 3 = [BLANK]
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor_int = random.randint(factor_int_min, factor_int_max)

                    # 生成小数（确保结果符合规则）
                    decimal_factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)

                    result = decimal_factor * factor_int

                    # 检查结果是否符合规则
                    if result_integer and result != int(result):
                        continue
                    if result_one_decimal_places and len(str(result).split('.')[-1]) != 1:
                        continue
                    if result_two_decimal_places and len(str(result).split('.')[-1]) > 2:
                        continue

                    stem = f"${format_decimal(decimal_factor)} \\times {factor_int} =$ [BLANK]"

                # ==================== 小数乘小数 ====================
                elif q_type == "multiply_decimal_decimal":
                    # 小数乘小数：0.5 × 0.3 = [BLANK]
                    decimal_places1 = random.randint(decimal_places_factor1, decimal_places_factor1_max)
                    decimal_places2 = random.randint(decimal_places_factor2, decimal_places_factor2_max)

                    factor1 = self._generate_decimal(decimal_places1, decimal_factor_min, decimal_factor_max)
                    factor2 = self._generate_decimal(decimal_places2, decimal_factor_min, decimal_factor_max)

                    result = factor1 * factor2

                    stem = f"${format_decimal(factor1)} \\times {format_decimal(factor2)} =$ [BLANK]"

                # ==================== 整数乘法运算定律推广到小数 ====================
                elif q_type == "multiply_commutative":
                    # 乘法交换律：0.5 × 2.4 = 2.4 × 0.5
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor1 = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    factor2 = random.randint(factor_int_min, factor_int_max)

                    stem = f"${format_decimal(factor1)} \\times {factor2} = {factor2} \\times \\text{{[BLANK]}}$"

                elif q_type == "multiply_associative":
                    # 乘法结合律：(0.5 × 2.4) × 4 = 0.5 × (2.4 × 4)
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor1 = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    factor2 = random.randint(2, 5)
                    factor3 = random.randint(2, 5)

                    stem = f"$({format_decimal(factor1)} \\times {factor2}) \\times {factor3} = {format_decimal(factor1)} \\times ({factor2} \\times \\text{{[BLANK]}})$"

                elif q_type == "multiply_distributive":
                    # 乘法分配律：0.5 × (2.4 + 3.6) = 0.5 × 2.4 + 0.5 × 3.6
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    add1 = random.randint(1, 10)
                    add2 = random.randint(1, 10)

                    stem = f"${format_decimal(factor)} \\times ({add1} + {add2}) = {format_decimal(factor)} \\times \\text{{[BLANK]}} + {format_decimal(factor)} \\times {add2}$"

                elif q_type == "multiply_distributive_fill":
                    # 乘法分配律填空：0.5 × 2.4 + 0.5 × 3.6 = 0.5 × (2.4 + 3.6)
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    add1 = random.randint(1, 10)
                    add2 = random.randint(1, 10)

                    stem = f"${format_decimal(factor)} \\times {add1} + {format_decimal(factor)} \\times {add2} = {format_decimal(factor)} \\times (\\text{{[BLANK]}} + {add2})$"

                # ==================== 小数除以整数 ====================
                elif q_type == "divide_decimal_int":
                    # 小数除以整数：3.6 ÷ 2 = [BLANK]
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    divisor = random.randint(divisor_min, divisor_max)

                    # 生成能整除的小数
                    quotient = random.randint(1, 20)
                    dividend = quotient * divisor

                    # 转换为小数
                    if decimal_places == 1:
                        dividend = dividend / 10
                    elif decimal_places == 2:
                        dividend = dividend / 100

                    stem = f"${format_decimal(dividend)} \\div {divisor} =$ [BLANK]"

                elif q_type == "divide_decimal_int_with_remainder":
                    # 小数除以整数（有余数，保留小数）：5.6 ÷ 2 = [BLANK]
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    divisor = random.randint(divisor_min, divisor_max)

                    dividend = self._generate_decimal(decimal_places, 1, 50)

                    stem = f"${format_decimal(dividend)} \\div {divisor} =$ [BLANK]"

                # ==================== 一个数除以小数 ====================
                elif q_type == "divide_int_decimal":
                    # 整数除以小数：10 ÷ 0.5 = [BLANK]
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)

                    # 生成能整除的情况
                    quotient = random.randint(2, 20)
                    divisor_dec = random.randint(1, 9) / (10 ** decimal_places)
                    dividend = quotient * divisor_dec

                    # 确保 dividend 是整数或简单小数
                    if dividend != int(dividend):
                        dividend = round(dividend, 1)

                    stem = f"${int(dividend) if dividend == int(dividend) else format_decimal(dividend)} \\div {format_decimal(divisor_dec)} =$ [BLANK]"

                elif q_type == "divide_decimal_decimal":
                    # 小数除以小数：3.6 ÷ 0.4 = [BLANK]
                    decimal_places_dividend = random.randint(decimal_places_min, decimal_places_max)
                    decimal_places_divisor = random.randint(1, 2)

                    # 生成能整除的情况
                    quotient = random.randint(2, 20)
                    divisor = random.randint(1, 9) / (10 ** decimal_places_divisor)
                    dividend = quotient * divisor

                    stem = f"${format_decimal(dividend)} \\div {format_decimal(divisor)} =$ [BLANK]"

                # ==================== 商的近似值 ====================
                elif q_type == "approximate_quotient":
                    # 商的近似值：10 ÷ 3 ≈ [BLANK]（保留两位小数）
                    dividend = random.randint(dividend_min, dividend_max)
                    divisor = random.randint(divisor_min, divisor_max)

                    # 确保不能整除
                    if dividend % divisor == 0:
                        divisor += 1

                    stem = f"${dividend} \\div {divisor} \\approx$ [BLANK]（保留{approximate_places}位小数）"

                elif q_type == "approximate_quotient_real":
                    # 商的近似值应用题：用四舍五入法求近似值
                    dividend = self._generate_decimal(random.randint(1, 2), 10, 100)
                    divisor = random.randint(divisor_min, divisor_max)

                    stem = f"${format_decimal(dividend)} \\div {divisor} \\approx$ [BLANK]（保留{approximate_places}位小数）"

                # ==================== 循环小数 ====================
                elif q_type == "repeating_decimal_identify":
                    # 识别循环小数：1 ÷ 3 = 0.333... = 0.[3]（用循环点表示）
                    # 常见的循环小数分数
                    repeating_fractions = [
                        (1, 3, "3"), (2, 3, "6"),  # 1/3 = 0.333..., 2/3 = 0.666...
                        (1, 6, "6"), (5, 6, "3"),  # 1/6 = 0.1666..., 5/6 = 0.8333...
                        (1, 7, "142857"), (2, 7, "285714"),  # 1/7, 2/7
                        (1, 9, "1"), (2, 9, "2"), (4, 9, "4"), (5, 9, "5"), (7, 9, "7"), (8, 9, "8"),
                        (1, 11, "09"), (2, 11, "18"), (3, 11, "27"), (4, 11, "36"),
                    ]

                    numerator, denominator, repeating_part = random.choice(repeating_fractions)

                    stem = f"${numerator} \\div {denominator} = 0.\\dot{{{repeating_part[0]}}}$ [BLANK] 循环小数"

                elif q_type == "repeating_decimal_write":
                    # 用循环小数表示商：1 ÷ 3 = [BLANK]
                    repeating_fractions = [
                        (1, 3, "3"), (2, 3, "6"),
                        (1, 7, "142857"), (2, 7, "285714"),
                        (1, 9, "1"), (2, 9, "2"), (4, 9, "4"), (5, 9, "5"),
                    ]

                    numerator, denominator, repeating_part = random.choice(repeating_fractions)

                    stem = f"${numerator} \\div {denominator} =$ [BLANK]（用循环小数表示）"

                # ==================== 小数乘除混合运算 ====================
                elif q_type == "multiply_divide_mixed":
                    # 小数乘除混合：0.5 × 4 ÷ 2 = [BLANK]
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    multiplier = random.randint(2, 10)
                    divisor = random.randint(2, 10)

                    stem = f"${format_decimal(factor)} \\times {multiplier} \\div {divisor} =$ [BLANK]"

                elif q_type == "multiply_multiply":
                    # 小数连乘：0.5 × 2 × 3 = [BLANK]
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor1 = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    factor2 = random.randint(2, 5)
                    factor3 = random.randint(2, 5)

                    stem = f"${format_decimal(factor1)} \\times {factor2} \\times {factor3} =$ [BLANK]"

                # ==================== 小数比较大小 ====================
                elif q_type == "compare_multiply_result":
                    # 乘法结果比较：0.5 × 3 [BLANK] 1.4
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    multiplier = random.randint(2, 10)

                    result = factor * multiplier
                    compare = result + random.uniform(-2, 2)

                    stem = f"${format_decimal(factor)} \\times {multiplier}$ [BLANK] ${format_decimal(compare)}$"

                elif q_type == "compare_divide_result":
                    # 除法结果比较：3.6 ÷ 2 [BLANK] 1.5
                    dividend = self._generate_decimal(random.randint(1, 2), 2, 20)
                    divisor = random.randint(2, 5)

                    result = dividend / divisor
                    compare = result + random.uniform(-1, 1)

                    stem = f"${format_decimal(dividend)} \\div {divisor}$ [BLANK] ${format_decimal(compare)}$"

                # ==================== 小数填空 ====================
                elif q_type == "fill_missing_factor":
                    # 填因数：[BLANK] × 3 = 1.5
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    multiplier = random.randint(2, 10)
                    result = factor * multiplier

                    stem = f"$\\text{{[BLANK]}} \\times {multiplier} = {format_decimal(result)}$"

                elif q_type == "fill_divisor":
                    # 填除数：3.6 ÷ [BLANK] = 1.2
                    divisor = random.randint(2, 10)
                    quotient = random.randint(2, 10)
                    dividend = divisor * quotient

                    # 转换为小数
                    decimal_places = random.randint(1, 2)
                    if decimal_places == 1:
                        dividend /= 10
                        quotient /= 10
                    elif decimal_places == 2:
                        dividend /= 100
                        quotient /= 100

                    stem = f"${format_decimal(dividend)} \\div \\text{{[BLANK]}} = {format_decimal(quotient)}$"

                else:
                    # 默认：小数乘整数
                    decimal_places = random.randint(decimal_places_min, decimal_places_max)
                    factor = self._generate_decimal(decimal_places, decimal_factor_min, decimal_factor_max)
                    multiplier = random.randint(2, 10)
                    stem = f"${format_decimal(factor)} \\times {multiplier} =$ [BLANK]"

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

    def _generate_decimal(self, decimal_places: int, min_val: float, max_val: float) -> float:
        """生成指定小数位数的随机小数"""
        multiplier = 10 ** decimal_places
        min_int = int(min_val * multiplier)
        max_int = int(max_val * multiplier)
        value = random.randint(min_int, max_int) / multiplier
        return round(value, decimal_places)

    def get_knowledge_points(self, template_config: dict, q_type: str = None) -> List[str]:
        """
        根据配置和题型动态返回知识点
        """
        # 支持通过配置自定义知识点
        if "knowledge_points" in template_config:
            return template_config["knowledge_points"]

        # 根据题型返回对应的知识点
        knowledge_map = {
            # 小数乘整数
            "multiply_decimal_int": ["小数乘整数", "小数乘法基础"],
            # 小数乘小数
            "multiply_decimal_decimal": ["小数乘小数", "小数乘法", "积的小数位数"],
            # 运算定律
            "multiply_commutative": ["乘法交换律", "运算定律推广到小数"],
            "multiply_associative": ["乘法结合律", "运算定律推广到小数"],
            "multiply_distributive": ["乘法分配律", "运算定律推广到小数"],
            "multiply_distributive_fill": ["乘法分配律", "逆向应用"],
            # 小数除法
            "divide_decimal_int": ["小数除以整数", "小数除法基础"],
            "divide_decimal_int_with_remainder": ["小数除以整数", "商的小数点"],
            "divide_int_decimal": ["一个数除以小数", "除数是小数的除法"],
            "divide_decimal_decimal": ["小数除以小数", "商不变的性质"],
            # 商的近似值
            "approximate_quotient": ["商的近似值", "四舍五入法"],
            "approximate_quotient_real": ["商的近似值", "实际应用"],
            # 循环小数
            "repeating_decimal_identify": ["循环小数的认识", "循环节"],
            "repeating_decimal_write": ["循环小数的表示", "商的形式"],
            # 混合运算
            "multiply_divide_mixed": ["小数乘除混合运算", "运算顺序"],
            "multiply_multiply": ["小数连乘", "乘法运算"],
            # 比较
            "compare_multiply_result": ["乘法结果比较", "小数大小比较"],
            "compare_divide_result": ["除法结果比较", "小数大小比较"],
            # 填空
            "fill_missing_factor": ["填因数", "逆向思维"],
            "fill_divisor": ["填除数", "逆向思维"],
        }

        if q_type and q_type in knowledge_map:
            return knowledge_map[q_type]

        return ["小数乘除综合练习"]

