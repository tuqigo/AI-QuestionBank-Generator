"""
模板：加减法统一生成器

统一支持所有加减法相关题型：
- 简单加减：5 + 3 = [BLANK]
- 连加：1+6+19=[BLANK]
- 连减：96-23-45=[BLANK]
- 加减混合：49-19+27=[BLANK]
- 减法填空：17 - [BLANK]= 2
- 运算比较：54+6+16[BLANK]74
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MixedAdditionSubtractionGenerator(TemplateGenerator):
    """加减法统一生成器 - 支持所有加减法题型"""

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

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        # 判断是否包含比较类型题目
        has_compare = any(t in question_complexity for t in ["compare_simple", "compare_with_result", "compare_mixed_operation"])

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
                    # 简单比较：a + b [BLANK]c
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    op = random.choice(["+", "-"])
                    if op == "-" and a < b:
                        continue
                    result = a + b if op == "+" else a - b
                    compare_type = random.choice(["equal", "greater", "less"])
                    if compare_type == "equal":
                        compare_num = result
                    elif compare_type == "greater":
                        compare_num = result + random.randint(1, 20)
                    else:
                        compare_num = result - random.randint(1, 20)
                        if compare_num < 0:
                            compare_num = result + random.randint(1, 20)
                    stem = f"{a}{op}{b}[BLANK]{compare_num}"

                elif q_type == "compare_with_result":
                    # 运算后比较（支持混合运算）：74-28+22[BLANK]75
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

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

            # 为比较类型题目设置 circle 答案样式
            question_rendering_meta = rendering_meta.copy()
            if q_type in ["compare_simple", "compare_with_result", "compare_mixed_operation"]:
                question_rendering_meta["answer_style"] = "circle"

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 3,
                "rendering_meta": question_rendering_meta,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["百以内加减法", "连加连减", "加减混合运算", "逆向思维"]
