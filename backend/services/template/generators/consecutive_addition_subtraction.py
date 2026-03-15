"""
模板 3：一年级 10 以内连加减法
生成逻辑：生成三个数和两个运算符，确保中间结果和最终结果都非负且<=10
例题：7 + 1 - 3 =（ ）
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class ConsecutiveAdditionSubtractionGenerator(TemplateGenerator):
    """连加减法生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        a_min = template_config.get("a", {}).get("min", 1)
        a_max = template_config.get("a", {}).get("max", 10)
        b_min = template_config.get("b", {}).get("min", 1)
        b_max = template_config.get("b", {}).get("max", 10)
        c_min = template_config.get("c", {}).get("min", 1)
        c_max = template_config.get("c", {}).get("max", 10)
        op1_values = template_config.get("op1", {}).get("values", ["+", "-"])
        op2_values = template_config.get("op2", {}).get("values", ["+", "-"])
        ensure_positive = "ensure_positive" in template_config.get("rules", [])
        result_within_10 = "result_within_10" in template_config.get("rules", [])

        for _ in range(quantity):
            max_attempts = 100
            for _ in range(max_attempts):
                a = random.randint(a_min, a_max)
                b = random.randint(b_min, b_max)
                c = random.randint(c_min, c_max)
                op1 = random.choice(op1_values)
                op2 = random.choice(op2_values)

                # 计算中间结果
                if op1 == "+":
                    intermediate = a + b
                else:
                    intermediate = a - b

                # 确保中间结果非负
                if ensure_positive and intermediate < 0:
                    continue

                # 计算最终结果
                if op2 == "+":
                    result = intermediate + c
                else:
                    result = intermediate - c

                # 确保最终结果非负
                if ensure_positive and result < 0:
                    continue

                # 确保结果在 10 以内
                if result_within_10 and result > 10:
                    continue

                stem = f"{a} {op1} {b} {op2} {c} = （    ）"

                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 3,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["10 以内连加连减运算"]
