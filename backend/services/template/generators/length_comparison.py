"""
模板：长度比较 - 长度单位换算
生成逻辑：生成米、分米、厘米之间的换算题目
例题：7m = [BLANK]cm、500cm = [BLANK]m、1dm = [BLANK]cm、70m2dm = [BLANK]dm
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class LengthComparisonGenerator(TemplateGenerator):
    """长度单位换算生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        value_max = template_config.get("value", {}).get("max", 100)
        value_min = template_config.get("value", {}).get("min", 1)
        convert_types = template_config.get("convert_types", [
            "m_to_cm", "cm_to_m",
            "dm_to_cm", "cm_to_dm",
            "m_to_dm", "dm_to_m",
            "m_cm_to_cm", "m_dm_to_dm"
        ])

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        for _ in range(quantity):
            max_attempts = 50
            for _ in range(max_attempts):
                # 随机选择换算类型
                convert_type = random.choice(convert_types)

                if convert_type == "m_to_cm":
                    # 米→厘米：1m = 100cm
                    # 例题：7m = [BLANK]cm
                    value = random.randint(value_min, value_max)
                    stem = f"{value}m = [BLANK]cm"
                    answer = value * 100

                elif convert_type == "cm_to_m":
                    # 厘米→米：100cm = 1m
                    # 例题：500cm = [BLANK]m
                    value = random.randint(1, value_max) * 100
                    stem = f"{value}cm = [BLANK]m"
                    answer = value // 100

                elif convert_type == "dm_to_cm":
                    # 分米→厘米：1dm = 10cm
                    # 例题：1dm = [BLANK]cm
                    value = random.randint(value_min, value_max)
                    stem = f"{value}dm = [BLANK]cm"
                    answer = value * 10

                elif convert_type == "cm_to_dm":
                    # 厘米→分米：10cm = 1dm
                    # 例题：30cm = [BLANK]dm
                    value = random.randint(1, value_max) * 10
                    stem = f"{value}cm = [BLANK]dm"
                    answer = value // 10

                elif convert_type == "m_to_dm":
                    # 米→分米：1m = 10dm
                    # 例题：5m = [BLANK]dm
                    value = random.randint(value_min, value_max)
                    stem = f"{value}m = [BLANK]dm"
                    answer = value * 10

                elif convert_type == "dm_to_m":
                    # 分米→米：10dm = 1m
                    # 例题：40dm = [BLANK]m
                    value = random.randint(1, value_max) * 10
                    stem = f"{value}dm = [BLANK]m"
                    answer = value // 10

                elif convert_type == "m_cm_to_cm":
                    # 米 + 厘米→厘米：1m50cm = [BLANK]cm
                    # 例题：2m50cm = [BLANK]cm
                    m_value = random.randint(value_min, value_max)
                    cm_value = random.randint(1, 99)
                    stem = f"{m_value}m{cm_value}cm = [BLANK]cm"
                    answer = m_value * 100 + cm_value

                elif convert_type == "m_dm_to_dm":
                    # 米 + 分米→分米：3m5dm = [BLANK]dm
                    # 例题：70m2dm = [BLANK]dm
                    m_value = random.randint(value_min, value_max)
                    dm_value = random.randint(1, 9)
                    stem = f"{m_value}m{dm_value}dm = [BLANK]dm"
                    answer = m_value * 10 + dm_value

                else:
                    # 默认：分米→厘米
                    value = random.randint(value_min, value_max)
                    stem = f"{value}dm = [BLANK]cm"
                    answer = value * 10

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
        return ["长度单位", "长度单位换算", "米分米厘米的认识"]
