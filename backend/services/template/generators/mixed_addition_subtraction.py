"""
模板：加减法统一生成器

统一支持所有加减法相关题型：
- 简单加减：5 + 3 = （ ）
- 连加：1+6+19=（ ）
- 连减：96-23-45=（ ）
- 加减混合：49-19+27=（ ）
- 减法填空：17 - （ ）= 2
- 运算比较：54+6+16（ ）74
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

        # 题型配置
        question_types = template_config.get("question_types", None)
        if question_types is None:
            # 旧格式兼容：根据是否有 op1/op2 判断
            if "op1" in template_config or "op2" in template_config:
                question_types = ["consecutive_add"]  # 连加减模式
            else:
                question_types = ["simple"]  # 简单加减模式

        # 规则配置
        ensure_positive = "ensure_positive" in template_config.get("rules", [])
        ensure_different = "ensure_different" in template_config.get("rules", [])
        result_within_10 = "result_within_10" in template_config.get("rules", [])
        result_within_100 = "result_within_100" in template_config.get("rules", [])
        result_limit = template_config.get("result_within", None)  # 自定义结果上限

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                # 随机选择题型
                q_type = random.choice(question_types)
                stem = ""

                if q_type == "simple":
                    # 简单加减：5 + 3 = （ ）
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

                    stem = f"{a}{op}{b}=（    ）"

                elif q_type == "simple_fill":
                    # 简单填空：5 + （ ） = 8  或  8 - （ ） = 3
                    op = random.choice(["+", "-"])
                    if op == "+":
                        a = random.randint(num_min, min(50, num_max))
                        missing = random.randint(num_min, min(50, num_max))
                        result = a + missing
                        if result_limit and result > result_limit:
                            continue
                        stem = f"{a}+（    ）={result}"
                    else:
                        result = random.randint(1, 50)
                        missing = random.randint(1, 50)
                        a = result + missing
                        if a > 100:
                            continue
                        stem = f"{a}-（    ）={result}"

                elif q_type == "consecutive_add":
                    # 连加：1+6+19=（ ）
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
                    stem = f"{a}+{b}+{c}=（    ）"

                elif q_type == "consecutive_subtract":
                    # 连减：96-23-45=（ ）
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
                    stem = f"{a}-{b}-{c}=（    ）"

                elif q_type == "mixed_operation":
                    # 加减混合：49-19+27=（ ）
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

                    stem = f"{a}{op1}{b}{op2}{c}=（    ）"

                elif q_type == "missing_operand":
                    # 减法填空：17 - （ ） = 2
                    result = random.randint(1, 50)
                    missing = random.randint(1, 50)
                    a = result + missing
                    if a > 100:
                        continue
                    stem = f"{a}-（    ）={result}"

                elif q_type == "compare_simple":
                    # 简单比较：a + b （ ）c
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
                    stem = f"{a}{op}{b}（    ）{compare_num}"

                elif q_type == "compare_with_result":
                    # 运算后比较（支持混合运算）：74-28+22（ ）75
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

                    stem = f"{a}{op1}{b}{op2}{c}（    ）{compare_num}"

                elif q_type == "compare_mixed_operation":
                    # 混合运算比较（确保有加有减）：74-28+22（ ）75
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

                    stem = f"{a}{op1}{b}{op2}{c}（    ）{compare_num}"

                else:
                    # 默认：简单加减法
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    op = random.choice(["+", "-"])
                    if ensure_positive and op == "-" and a < b:
                        continue
                    stem = f"{a}{op}{b}=（    ）"

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

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["百以内加减法", "连加连减", "加减混合运算", "逆向思维"]
