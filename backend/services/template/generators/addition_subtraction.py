"""
模板 2：一年级 10 以内的加减法
生成逻辑：生成两个数和运算符，确保减法结果非负
例题：2 + 2 =（ ）
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class AdditionSubtractionGenerator(TemplateGenerator):
    """加减法生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        a_min = template_config.get("a", {}).get("min", 1)
        a_max = template_config.get("a", {}).get("max", 10)
        b_min = template_config.get("b", {}).get("min", 1)
        b_max = template_config.get("b", {}).get("max", 10)
        operators = template_config.get("op", {}).get("values", ["+", "-"])
        ensure_positive = "ensure_positive" in template_config.get("rules", [])

        for _ in range(quantity):
            max_attempts = 50
            for attempt in range(max_attempts):
                a = random.randint(a_min, a_max)
                b = random.randint(b_min, b_max)
                op = random.choice(operators)

                # 确保减法结果非负
                if ensure_positive and op == "-" and a < b:
                    continue

                stem = f"{a} {op} {b} = （    ）"

                if stem in used_stems:
                    continue

                used_stems.add(stem)
                break
            else:
                # 50 次尝试后仍未生成有效题目，跳过
                continue

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 3,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["10 以内加减法"]
