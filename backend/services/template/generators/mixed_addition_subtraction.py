"""
模板：加减法统一生成器

统一支持所有加减法相关题型：
- 简单加减：5 + 3 = [BLANK]
- 连加：1+6+19=[BLANK]
- 连减：96-23-45=[BLANK]
- 加减混合：49-19+27=[BLANK]
- 减法填空：17 - [BLANK]= 2
- 运算比较：54+6+16[BLANK]74
- 简单比大小：4[BLANK]5
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MixedAdditionSubtractionGenerator(TemplateGenerator):
    """加减法统一生成器 - 支持所有加减法及比大小题型"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置 - 支持新旧两种格式
        # 旧格式兼容：a, b, c 单独配置
        a_min = template_config.get("a", {}).get("min", 1)
        a_max = template_config.get("a", {}).get("max", 10)
        b_min = template_config.get("b", {}).get("min", 1)
        b_max = template_config.get("b", {}).get("max", 10)
        c_min = template_config.get("c", {}).get("min", 1)
        c_max = template_config.get("c", {}).get("max", 10)

        # 新格式
        num_min = template_config.get("num", {}).get("min", a_min)
        num_max = template_config.get("num", {}).get("max", a_max)

        # 运算符配置
        op_values = template_config.get("op", {}).get("values", ["+", "-"])
        op1_values = template_config.get("op1", {}).get("values", ["+", "-"])
        op2_values = template_config.get("op2", {}).get("values", ["+", "-"])

        # 题型复杂度配置（支持新旧两种格式）
        # 新格式：question_complexity（避免与 generate() 的 question_type 参数混淆）
        # 旧格式：question_types（兼容已有数据库配置）
        question_complexity = template_config.get("question_complexity", None)
        if question_complexity is None:
            # 尝试旧格式兼容
            question_complexity = template_config.get("question_types", None)
        if question_complexity is None:
            # 默认：根据是否有 op1/op2 判断
            if "op1" in template_config or "op2" in template_config:
                question_complexity = ["consecutive_add"]  # 连加减模式
            else:
                question_complexity = ["simple"]  # 简单加减模式

        # 规则配置
        ensure_positive = "ensure_positive" in template_config.get("rules", [])
        ensure_different = "ensure_different" in template_config.get("rules", [])
        result_within_10 = "result_within_10" in template_config.get("rules", [])
        result_within_100 = "result_within_100" in template_config.get("rules", [])
        result_limit = template_config.get("result_within", None)  # 自定义结果上限
        ensure_no_carrying = template_config.get("ensure_no_carrying", False)  # 加法不进位（个位和十位都不进位）

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        # 支持通过 q_type 设置 answer_style（优先级高于 rendering_config）
        # q_type 格式：题型：answer_style，例如："COMPARE_SIMPLE:circle"
        q_type_styles = template_config.get("q_type", {})
        if isinstance(q_type_styles, str):
            # 兼容简单字符串格式
            q_type_styles = {q_type_styles: "circle"}

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                # 随机选择题型复杂度
                q_type = random.choice(question_complexity)
                stem = ""

                if q_type == "simple":
                    # 简单加减：5 + 3 = [BLANK]
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    op = random.choice(op_values)

                    if ensure_positive and op == "-" and a < b:
                        continue
                    if ensure_different and a == b:
                        continue

                    # 检查不进位约束（仅加法）
                    if ensure_no_carrying and op == "+":
                        # 个位相加不能进位
                        if (a % 10) + (b % 10) >= 10:
                            continue
                        # 十位相加不能进位
                        if (a // 10) + (b // 10) >= 10:
                            continue

                    result = a + b if op == "+" else a - b
                    if result_limit and result > result_limit:
                        continue
                    if result_within_10 and result > 10:
                        continue
                    if result_within_100 and result > 100:
                        continue

                    stem = f"{a}{op}{b}=[BLANK]"

                elif q_type == "simple_fill":
                    # 简单填空：5 + [BLANK] = 8  或  8 - [BLANK] = 3
                    op = random.choice(["+", "-"])
                    if op == "+":
                        a = random.randint(num_min, min(50, num_max))
                        missing = random.randint(num_min, min(50, num_max))
                        result = a + missing
                        if result_limit and result > result_limit:
                            continue
                        stem = f"{a}+[BLANK]={result}"
                    else:
                        result = random.randint(1, 50)
                        missing = random.randint(1, 50)
                        a = result + missing
                        if a > 100:
                            continue
                        stem = f"{a}-[BLANK]={result}"

                elif q_type == "consecutive_add":
                    # 连加：1+6+19=[BLANK]
                    # 根据 result_within_10 调整范围
                    if result_within_10:
                        a = random.randint(num_min, min(4, a_max if a_max > 0 else 10))
                        b = random.randint(num_min, min(3, max(3, a_max - a if a_max > a else 10 - a)))
                        c = random.randint(num_min, min(3, max(3, a_max - a - b if a_max > a + b else 10 - a - b)))
                    else:
                        a = random.randint(num_min, min(50, max(num_min, num_max - 20)))
                        b = random.randint(1, min(30, max(1, num_max - a - 1)))
                        c = random.randint(1, min(30, max(1, num_max - a - b)))

                    result = a + b + c
                    if result_within_10 and result > 10:
                        continue
                    if result_within_100 and result > 100:
                        continue
                    stem = f"{a}+{b}+{c}=[BLANK]"

                elif q_type == "consecutive_subtract":
                    # 连减：96-23-45=[BLANK]
                    if result_within_10:
                        # 10 以内连减
                        a = random.randint(max(3, num_min), min(10, a_max if a_max > 0 else 10))
                        b = random.randint(num_min, min(3, max(num_min, a - 2)))
                        c = random.randint(num_min, max(num_min, a - b - 1))
                    else:
                        c = random.randint(num_min, min(30, num_max))
                        b = random.randint(num_min, min(30, max(num_min, num_max - c)))
                        a = random.randint(max(b + c, 20), min(100, b + c + 50))

                    if ensure_positive and (a - b - c < 0):
                        continue
                    stem = f"{a}-{b}-{c}=[BLANK]"

                elif q_type == "mixed_operation":
                    # 加减混合：49-19+27=[BLANK]
                    a = random.randint(20, min(80, num_max))
                    b = random.randint(1, min(50, num_max))
                    c = random.randint(1, min(50, num_max))
                    op1 = random.choice(op1_values)
                    op2 = random.choice(op2_values)

                    if op1 == "+":
                        temp = a + b
                    else:
                        temp = a - b
                        if ensure_positive and temp < 0:
                            continue

                    if op2 == "+":
                        result = temp + c
                    else:
                        result = temp - c
                        if ensure_positive and result < 0:
                            continue

                    if result_within_10 and result > 10:
                        continue
                    if result_within_100 and result > 100:
                        continue
                    if result < 0:
                        continue

                    stem = f"{a}{op1}{b}{op2}{c}=[BLANK]"

                elif q_type == "missing_operand":
                    # 减法填空：17 - [BLANK]= 2
                    result = random.randint(1, 50)
                    missing = random.randint(1, 50)
                    a = result + missing
                    if a > 100:
                        continue
                    stem = f"{a}-[BLANK]={result}"

                elif q_type == "compare_simple":
                    # 简单比较：a [BLANK] b
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    if ensure_different and a == b:
                        continue
                    stem = f"{a}[BLANK]{b}"

                elif q_type == "compare_with_result":
                    # 运算后比较（支持混合运算）：74-28+22[BLANK]75
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

                    # 根据 result_within_10 调整数字范围
                    if result_within_10:
                        # 10 以内运算：单个数字或简单两步运算
                        # 简化为单步运算比较：2+4○7
                        a = random.randint(num_min, min(10, num_max))
                        b = random.randint(num_min, min(10, num_max))
                        op = random.choice(op_values)

                        if op == "+":
                            result = a + b
                        else:
                            result = a - b
                            if ensure_positive and result < 0:
                                continue

                        if result > 10:
                            continue

                        compare_type = random.choice(["equal", "greater", "less"])
                        if compare_type == "equal":
                            compare_num = result
                        elif compare_type == "greater":
                            compare_num = result + random.randint(1, 3)
                        else:
                            compare_num = result - random.randint(1, 3)
                            if compare_num < 0:
                                compare_num = result + random.randint(1, 3)

                        stem = f"{a}{op}{b}[BLANK]{compare_num}"
                    else:
                        # 100 以内运算
                        a = random.randint(20, 80)
                        b = random.randint(10, 50)
                        c = random.randint(10, 50)

                        if op1 == "+":
                            temp = a + b
                        else:
                            temp = a - b
                            if ensure_positive and temp < 0:
                                continue

                        if op2 == "+":
                            result = temp + c
                        else:
                            result = temp - c
                            if ensure_positive and result < 0:
                                continue

                        if result_within_100 and result > 100:
                            continue
                        if result < 0:
                            continue

                        compare_type = random.choice(["equal", "greater", "less"])
                        if compare_type == "equal":
                            compare_num = result
                        elif compare_type == "greater":
                            compare_num = result + random.randint(1, 20)
                        else:
                            compare_num = result - random.randint(1, 20)
                            if compare_num < 0:
                                compare_num = result + random.randint(1, 20)

                        stem = f"{a}{op1}{b}{op2}{c}[BLANK]{compare_num}"

                elif q_type == "compare_mixed_operation":
                    # 混合运算比较（确保有加有减）：74-28+22[BLANK]75
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

                    # 确保至少有一个加法和一个减法
                    if op1 == op2:
                        op1 = "-"
                        op2 = "+"

                    a = random.randint(30, 90)
                    b = random.randint(10, 50)
                    c = random.randint(10, 40)

                    if op1 == "+":
                        temp = a + b
                    else:
                        temp = a - b
                        if ensure_positive and temp < 0:
                            continue

                    if op2 == "+":
                        result = temp + c
                    else:
                        result = temp - c
                        if ensure_positive and result < 0:
                            continue

                    if result_within_100 and result > 100:
                        continue
                    if result < 0:
                        continue

                    compare_type = random.choice(["equal", "greater", "less"])
                    if compare_type == "equal":
                        compare_num = result
                    elif compare_type == "greater":
                        compare_num = result + random.randint(1, 20)
                    else:
                        compare_num = result - random.randint(1, 20)
                        if compare_num < 0:
                            compare_num = result + random.randint(1, 20)

                    stem = f"{a}{op1}{b}{op2}{c}[BLANK]{compare_num}"

                else:
                    # 默认：简单加减法
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    op = random.choice(["+", "-"])
                    if ensure_positive and op == "-" and a < b:
                        continue
                    stem = f"{a}{op}{b}=[BLANK]"

                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                # 100 次尝试后仍未生成有效题目，跳过
                continue

            # 应用 q_type 级别的 answer_style 配置（优先级高于 rendering_config）
            question_rendering_meta = rendering_meta.copy()
            if q_type in q_type_styles:
                question_rendering_meta["answer_style"] = q_type_styles[q_type]

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 3,
                "rendering_meta": question_rendering_meta,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        points = ["百以内加减法"]

        # 根据配置添加细分知识点
        if template_config.get("ensure_no_carrying", False):
            points.append("两位数加两位数（不进位）")
        if "consecutive_add" in template_config.get("question_complexity", []):
            points.append("连加")
        if "consecutive_subtract" in template_config.get("question_complexity", []):
            points.append("连减")
        if "mixed_operation" in template_config.get("question_complexity", []):
            points.append("加减混合运算")
        if "missing_operand" in template_config.get("question_complexity", []):
            points.append("逆向思维")
        if "compare_simple" in template_config.get("question_complexity", []):
            points.append("数的大小比较")

        return points
