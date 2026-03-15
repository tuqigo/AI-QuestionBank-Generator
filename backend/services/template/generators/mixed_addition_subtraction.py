"""
模板：连加、连减及加减综合
生成逻辑：支持多种题型的百以内加减法综合练习
例题：
  - 连加：1+6+19=（）
  - 减法填空：17 - （）= 2
  - 连减：96-23-45=（）
  - 比较大小：54+6+16（）74
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MixedAdditionSubtractionGenerator(TemplateGenerator):
    """连加、连减及加减综合生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        num_min = template_config.get("num", {}).get("min", 1)
        num_max = template_config.get("num", {}).get("max", 100)
        question_types = template_config.get("question_types", [
            "consecutive_add",
            "consecutive_subtract",
            "mixed_operation",
            "missing_operand",
            "compare_with_result",
            "compare_mixed_operation",
        ])
        ensure_positive = "ensure_positive" in template_config.get("rules", [])
        result_within_100 = "result_within_100" in template_config.get("rules", [])

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                # 随机选择题型
                q_type = random.choice(question_types)
                stem = ""

                if q_type == "consecutive_add":
                    # 连加：1+6+19=（）
                    a = random.randint(num_min, min(num_max - 50, 50))
                    b = random.randint(1, min(50, num_max - a - 1))
                    c = random.randint(1, min(50, num_max - a - b))
                    if result_within_100 and (a + b + c) > 100:
                        continue
                    stem = f"{a}+{b}+{c}=（    ）"

                elif q_type == "consecutive_subtract":
                    # 连减：96-23-45=（）
                    c = random.randint(num_min, min(50, num_max))
                    b = random.randint(num_min, min(50, num_max - c))
                    a = random.randint(max(b + c, 50), min(100, b + c + 50))
                    if ensure_positive and (a - b - c < 0):
                        continue
                    stem = f"{a}-{b}-{c}=（    ）"

                elif q_type == "mixed_operation":
                    # 加减混合：25+30-15=（）
                    a = random.randint(20, min(80, num_max))
                    b = random.randint(1, min(50, num_max - a))
                    c = random.randint(1, min(50, a + b))
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

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

                    stem = f"{a}{op1}{b}{op2}{c}=（    ）"

                elif q_type == "missing_operand":
                    # 减法填空：17 - （）= 2
                    result = random.randint(1, 50)
                    missing = random.randint(1, 50)
                    a = result + missing
                    if a > 100:
                        continue
                    stem = f"{a}-（    ）={result}"

                elif q_type == "compare_with_result":
                    # 比较大小：54+6+16（）74  或  74-28+22（）75
                    # 随机选择运算符组合
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

                    # 根据运算符生成数字
                    a = random.randint(20, 80)
                    b = random.randint(10, 50)
                    c = random.randint(10, 50)

                    # 计算中间结果
                    if op1 == "+":
                        temp = a + b
                    else:
                        temp = a - b
                        if ensure_positive and temp < 0:
                            continue

                    # 计算最终结果
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

                    # 随机生成比较的数（可能等于、大于或小于结果）
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
                    # 混合运算比较：74-28+22（）75  或  74-28-22（）40
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

                    # 确保至少有一个加法和一个减法，形成混合运算
                    if op1 == op2:
                        op1 = "-"
                        op2 = "+"

                    a = random.randint(30, 90)
                    b = random.randint(10, 50)
                    c = random.randint(10, 40)

                    # 计算中间结果
                    if op1 == "+":
                        temp = a + b
                    else:
                        temp = a - b
                        if ensure_positive and temp < 0:
                            continue

                    # 计算最终结果
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

                    # 随机生成比较的数
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
