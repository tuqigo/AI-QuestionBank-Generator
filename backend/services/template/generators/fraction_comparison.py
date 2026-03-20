"""
模板：分数比大小
生成逻辑：生成两个分数，比较它们的大小
例题：$\\frac{3}{4}$ [BLANK] $\\frac{2}{3}$、$\\frac{5}{6}$ [BLANK] $\\frac{7}{8}$
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class FractionComparisonGenerator(TemplateGenerator):
    """分数比大小生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        denominator_min = template_config.get("denominator", {}).get("min", 2)
        denominator_max = template_config.get("denominator", {}).get("max", 10)
        numerator_min = template_config.get("numerator", {}).get("min", 1)
        numerator_max = template_config.get("numerator", {}).get("max", None)  # None 表示跟随分母
        compare_types = template_config.get("compare_types", ["common_denominator", "common_numerator", "different"])
        rules = template_config.get("rules", [])
        ensure_different = "ensure_different" in rules
        ensure_proper_fraction = "ensure_proper_fraction" in rules  # 确保是真分数（分子<分母）

        # 获取渲染元数据，并覆盖 answer_style 为 circle（比大小题目专用）
        rendering_meta = self.get_rendering_meta(question_type, template_config)
        rendering_meta["answer_style"] = "circle"
        rendering_meta["answer_width"] = 40  # 圆圈宽度

        for _ in range(quantity):
            max_attempts = 50
            for _ in range(max_attempts):
                # 随机选择比较类型
                compare_type = random.choice(compare_types)

                if compare_type == "common_denominator":
                    # 同分母分数比较：2/5 [BLANK] 3/5
                    denominator = random.randint(denominator_min, denominator_max)
                    numerator1 = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)
                    numerator2 = random.randint(numerator_min, denominator - 1 if ensure_proper_fraction else denominator)

                    if ensure_different and numerator1 == numerator2:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator}}}$ [BLANK] $\\frac{{{numerator2}}}{{{denominator}}}$"

                elif compare_type == "common_numerator":
                    # 同分子分数比较：2/3 [BLANK] 2/5
                    numerator = random.randint(numerator_min, denominator_max)
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)

                    if ensure_different and denominator1 == denominator2:
                        continue
                    if ensure_proper_fraction and (numerator >= denominator1 or numerator >= denominator2):
                        continue

                    stem = f"$\\frac{{{numerator}}}{{{denominator1}}}$ [BLANK] $\\frac{{{numerator}}}{{{denominator2}}}$"

                else:
                    # 异分母分数比较：3/4 [BLANK] 2/3
                    denominator1 = random.randint(denominator_min, denominator_max)
                    denominator2 = random.randint(denominator_min, denominator_max)

                    if ensure_different and denominator1 == denominator2:
                        continue

                    max_num1 = denominator1 - 1 if ensure_proper_fraction else denominator1
                    max_num2 = denominator2 - 1 if ensure_proper_fraction else denominator2

                    numerator1 = random.randint(numerator_min, max_num1)
                    numerator2 = random.randint(numerator_min, max_num2)

                    # 检查是否相等（交叉相乘）
                    if numerator1 * denominator2 == numerator2 * denominator1:
                        continue

                    stem = f"$\\frac{{{numerator1}}}{{{denominator1}}}$ [BLANK] $\\frac{{{numerator2}}}{{{denominator2}}}$"

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
                "rows_to_answer": 1,
                "rendering_meta": rendering_meta,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["分数的意义", "分数的大小比较", "通分"]
