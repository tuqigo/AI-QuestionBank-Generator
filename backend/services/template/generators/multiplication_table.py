"""
模板：九九乘法表练习
生成逻辑：生成 1-9 的乘法算式
例题：3 × 4 =（ ）
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MultiplicationTableGenerator(TemplateGenerator):
    """九九乘法表生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 配置范围
        min_factor = template_config.get("min_factor", 1)
        max_factor = template_config.get("max_factor", 9)

        # 是否只生成特定数字的乘法（例如只生成 3 的乘法）
        fixed_first = template_config.get("fixed_first", None)

        # 是否交换因子位置（例如 3×4 和 4×3 都出现）
        allow_commute = template_config.get("allow_commute", False)

        for _ in range(quantity):
            max_attempts = 50
            for attempt in range(max_attempts):
                # 如果指定了第一个因子，则固定使用它
                if fixed_first is not None:
                    a = fixed_first
                else:
                    a = random.randint(min_factor, max_factor)

                b = random.randint(min_factor, max_factor)

                # 如果不允许交换，确保 a <= b 避免重复
                if not allow_commute and a > b:
                    a, b = b, a

                stem = f"{a} × {b} = （    ）"

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
        return ["九九乘法表", "乘法运算"]
