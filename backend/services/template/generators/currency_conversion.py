"""
模板：认识人民币 - 元角分换算
生成逻辑：生成元、角、分之间的换算题目
例题：50 分 = [BLANK]角、6 元 = [BLANK]角、54 元 50 分 = [BLANK]分
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class CurrencyConversionGenerator(TemplateGenerator):
    """人民币换算生成器"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置
        yuan_max = template_config.get("yuan", {}).get("max", 50)
        jiao_max = template_config.get("jiao", {}).get("max", 50)
        fen_max = template_config.get("fen", {}).get("max", 50)
        convert_types = template_config.get("convert_types", ["yuan_to_jiao", "jiao_to_fen", "yuan_fen_to_fen"])

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        for _ in range(quantity):
            max_attempts = 50
            for _ in range(max_attempts):
                # 随机选择换算类型
                convert_type = random.choice(convert_types)

                if convert_type == "yuan_to_jiao":
                    # 元→角：6 元 = [BLANK]角
                    yuan = random.randint(1, yuan_max)
                    stem = f"{yuan}元 = [BLANK]角"
                    answer = yuan * 10

                elif convert_type == "jiao_to_yuan":
                    # 角→元：60 角 = [BLANK]元
                    jiao = random.randint(10, jiao_max) - (random.randint(1, jiao_max) % 10)
                    if jiao < 10:
                        jiao = 10
                    stem = f"{jiao}角 = [BLANK]元"
                    answer = jiao // 10

                elif convert_type == "jiao_to_fen":
                    # 角→分：5 角 = [BLANK]分
                    jiao = random.randint(1, jiao_max)
                    stem = f"{jiao}角 = [BLANK]分"
                    answer = jiao * 10

                elif convert_type == "fen_to_jiao":
                    # 分→角：50 分 = [BLANK]角
                    fen = random.randint(10, fen_max) - (random.randint(1, fen_max) % 10)
                    if fen < 10:
                        fen = 10
                    stem = f"{fen}分 = [BLANK]角"
                    answer = fen // 10

                elif convert_type == "yuan_to_fen":
                    # 元→分：5 元 = [BLANK]分
                    yuan = random.randint(1, yuan_max)
                    stem = f"{yuan}元 = [BLANK]分"
                    answer = yuan * 100

                elif convert_type == "fen_to_yuan":
                    # 分→元：100 分 = [BLANK]元
                    fen = random.randint(100, fen_max * 10) - (random.randint(1, fen_max * 10) % 100)
                    if fen < 100:
                        fen = 100
                    stem = f"{fen}分 = [BLANK]元"
                    answer = fen // 100

                elif convert_type == "yuan_jiao_to_jiao":
                    # 元 + 角→角：3 元 5 角 = [BLANK]角
                    yuan = random.randint(1, yuan_max)
                    jiao = random.randint(1, 9)
                    stem = f"{yuan}元{jiao}角 = [BLANK]角"
                    answer = yuan * 10 + jiao

                elif convert_type == "yuan_fen_to_fen":
                    # 元 + 分→分：54 元 50 分 = [BLANK]分
                    yuan = random.randint(1, yuan_max)
                    fen = random.randint(10, 99)
                    stem = f"{yuan}元{fen}分 = [BLANK]分"
                    answer = yuan * 100 + fen

                elif convert_type == "yuan_jiao_fen_to_fen":
                    # 元 + 角 + 分→分：3 元 5 角 20 分 = [BLANK]分
                    yuan = random.randint(1, yuan_max)
                    jiao = random.randint(1, 9)
                    fen = random.randint(10, 99)
                    stem = f"{yuan}元{jiao}角{fen}分 = [BLANK]分"
                    answer = yuan * 100 + jiao * 10 + fen

                else:
                    # 默认：分→角
                    fen = random.randint(10, fen_max) - (random.randint(1, fen_max) % 10)
                    if fen < 10:
                        fen = 10
                    stem = f"{fen}分 = [BLANK]角"
                    answer = fen // 10

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
        return ["认识人民币", "元角分的换算"]
