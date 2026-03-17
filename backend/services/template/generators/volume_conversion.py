"""
模板：长方体和正方体体积单位的换算
生成逻辑：生成体积单位之间的换算题目（立方米、立方分米、立方厘米、升、毫升）
例题：5 立方米 = （ ）立方分米、3000 立方厘米 = （ ）立方分米
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class VolumeConversionGenerator(TemplateGenerator):
    """体积单位换算生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        volume_max = template_config.get("volume", {}).get("max", 100)
        volume_min = template_config.get("volume", {}).get("min", 1)
        convert_types = template_config.get("convert_types", [
            "m3_to_dm3", "dm3_to_cm3", "cm3_to_dm3", "dm3_to_m3",
            "l_to_ml", "ml_to_l", "dm3_to_l", "l_to_dm3"
        ])

        for _ in range(quantity):
            max_attempts = 50
            for _ in range(max_attempts):
                # 随机选择换算类型
                convert_type = random.choice(convert_types)

                if convert_type == "m3_to_dm3":
                    # 立方米→立方分米：1 立方米 = 1000 立方分米
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}立方米 = （    ）立方分米"
                    answer = value * 1000

                elif convert_type == "dm3_to_m3":
                    # 立方分米→立方米：1000 立方分米 = 1 立方米
                    value = random.randint(1, volume_max) * 1000
                    stem = f"{value}立方分米 = （    ）立方米"
                    answer = value // 1000

                elif convert_type == "dm3_to_cm3":
                    # 立方分米→立方厘米：1 立方分米 = 1000 立方厘米
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}立方分米 = （    ）立方厘米"
                    answer = value * 1000

                elif convert_type == "cm3_to_dm3":
                    # 立方厘米→立方分米：1000 立方厘米 = 1 立方分米
                    value = random.randint(1, volume_max) * 1000
                    stem = f"{value}立方厘米 = （    ）立方分米"
                    answer = value // 1000

                elif convert_type == "l_to_ml":
                    # 升→毫升：1 升 = 1000 毫升
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}升 = （    ）毫升"
                    answer = value * 1000

                elif convert_type == "ml_to_l":
                    # 毫升→升：1000 毫升 = 1 升
                    value = random.randint(1, volume_max) * 1000
                    stem = f"{value}毫升 = （    ）升"
                    answer = value // 1000

                elif convert_type == "dm3_to_l":
                    # 立方分米→升：1 立方分米 = 1 升
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}立方分米 = （    ）升"
                    answer = value

                elif convert_type == "l_to_dm3":
                    # 升→立方分米：1 升 = 1 立方分米
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}升 = （    ）立方分米"
                    answer = value

                elif convert_type == "cm3_to_ml":
                    # 立方厘米→毫升：1 立方厘米 = 1 毫升
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}立方厘米 = （    ）毫升"
                    answer = value

                elif convert_type == "ml_to_cm3":
                    # 毫升→立方厘米：1 毫升 = 1 立方厘米
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}毫升 = （    ）立方厘米"
                    answer = value

                elif convert_type == "m3_to_l":
                    # 立方米→升：1 立方米 = 1000 升
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}立方米 = （    ）升"
                    answer = value * 1000

                elif convert_type == "l_to_m3":
                    # 升→立方米：1000 升 = 1 立方米
                    value = random.randint(1, volume_max) * 1000
                    stem = f"{value}升 = （    ）立方米"
                    answer = value // 1000

                else:
                    # 默认：立方分米→立方厘米
                    value = random.randint(volume_min, volume_max)
                    stem = f"{value}立方分米 = （    ）立方厘米"
                    answer = value * 1000

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
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        return ["体积单位", "体积单位换算", "长方体和正方体"]
