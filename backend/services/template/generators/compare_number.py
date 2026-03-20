"""
模板 1：一年级 10 以内的数比一比
生成逻辑：生成两个数，用括号表示比较大小
例题：4（）5
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class CompareNumberGenerator(TemplateGenerator):
    """比一比大小生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_pairs = set()

        a_min = template_config.get("a", {}).get("min", 1)
        a_max = template_config.get("a", {}).get("max", 10)
        b_min = template_config.get("b", {}).get("min", 1)
        b_max = template_config.get("b", {}).get("max", 10)
        ensure_different = "ensure_different" in template_config.get("rules", [])

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        for _ in range(quantity):
            # 生成不重复的数对
            max_attempts = 50
            for attempt in range(max_attempts):
                a = random.randint(a_min, a_max)
                b = random.randint(b_min, b_max)

                if ensure_different and a == b:
                    continue

                pair = (a, b)
                if pair in used_pairs:
                    continue

                used_pairs.add(pair)
                break
            else:
                # 50 次尝试后仍未生成有效题目，跳过
                continue

            # 构建题干
            stem = f"{a}[BLANK]{b}"

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 1,
                "rendering_meta": rendering_meta,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["数的大小比较"]
