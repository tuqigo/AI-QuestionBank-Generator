"""
模板：加减法统一生成器

统一支持所有加减法相关题型：
- 简单加减：5 + 3 = [BLANK]
- 连加：1+6+19=[BLANK]
- 连减：96-23-45=[BLANK]
- 加减混合：49-19+27=[BLANK]
- 减法填空：17 - [BLANK]= 2
- 运算比较：54+6+16[BLANK]74
- 简单比大小：4[BLANK]5
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class MixedAdditionSubtractionGenerator(TemplateGenerator):
    """加减法统一生成器 - 支持所有加减法及比大小题型"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()
        # 当所有唯一题目用尽后，允许重复生成
        allow_duplicate = False

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

        # 题型复杂度配置（支持新旧两种格式）
        # 新格式：question_complexity（避免与 generate() 的 question_type 参数混淆）
        # 旧格式：question_types（兼容已有数据库配置）
        question_complexity = template_config.get("question_complexity", None)
        if question_complexity is None:
            # 尝试旧格式兼容
            question_complexity = template_config.get("question_types", None)
        if question_complexity is None:
            # 默认：根据是否有 op1/op2 判断
            if "op1" in template_config or "op2" in template_config:
                question_complexity = ["consecutive_add"]  # 连加减模式
            else:
                question_complexity = ["simple"]  # 简单加减模式

        # 规则配置
        ensure_positive = "ensure_positive" in template_config.get("rules", [])
        ensure_different = "ensure_different" in template_config.get("rules", [])
        result_within_10 = "result_within_10" in template_config.get("rules", [])
        result_within_100 = "result_within_100" in template_config.get("rules", [])
        result_within_20 = "result_within_20" in template_config.get("rules", [])
        result_limit = template_config.get("result_within", None)  # 自定义结果上限
        min_result = template_config.get("min_result", None)  # 自定义结果下限
        ensure_no_carrying = template_config.get("ensure_no_carrying", False)  # 加法不进位（个位和十位都不进位）

        # fixed_addend 配置：固定一个加数为指定值（用于 9 加几、876 加几、5432 加几等）
        fixed_addend = template_config.get("fixed_addend", None)
        # fixed_subtractor 配置：固定减数（用于十几减 9 等）
        fixed_subtractor = template_config.get("fixed_subtractor", None)

        # 获取渲染元数据
        rendering_meta = self.get_rendering_meta(question_type, template_config)

        # 支持通过 q_type 设置 answer_style（优先级高于 rendering_config）
        # q_type 格式：题型：answer_style，例如："COMPARE_SIMPLE:circle"
        q_type_styles = template_config.get("q_type", {})
        if isinstance(q_type_styles, str):
            # 兼容简单字符串格式
            q_type_styles = {q_type_styles: "circle"}

        # 用于记录已尝试的 (q_type, stem) 组合，判断是否所有组合都已用尽
        all_possible_attempts = set()
        max_total_attempts = quantity * 50  # 总体尝试上限，防止死循环

        for _ in range(quantity):
            max_attempts = 100
            generated = False

            for attempt in range(max_attempts):
                # 如果总体尝试次数过多，允许重复
                if len(all_possible_attempts) > max_total_attempts:
                    allow_duplicate = True
                    used_stems.clear()  # 清空已用题目，允许重复

                # 随机选择题型复杂度
                q_type = random.choice(question_complexity)
                stem = ""

                if q_type == "simple":
                    # 简单加减：5 + 3 = [BLANK]
                    op = random.choice(op_values)

                    # 如果配置了 fixed_addend，固定一个加数（用于 9 加几、876 加几、5432 加几等）
                    if fixed_addend and op == "+":
                        op = "+"  # 确保是加法
                        # 确保 fixed_addend 是列表
                        if not isinstance(fixed_addend, list):
                            fixed_addend = [fixed_addend]
                        # 第一个加数从固定值中选择（确保是 9+? 而不是 ?+9）
                        a = random.choice(fixed_addend)
                        b = random.randint(num_min, num_max)
                    # 如果配置了 fixed_subtractor，固定减数（用于十几减 9 等）
                    elif fixed_subtractor and op == "-":
                        op = "-"  # 确保是减法
                        a = random.randint(num_min, num_max)
                        b = fixed_subtractor  # 固定减数
                    else:
                        a = random.randint(num_min, num_max)
                        b = random.randint(num_min, num_max)

                    if ensure_positive and op == "-" and a < b:
                        continue
                    if ensure_different and a == b:
                        continue

                    # 检查不进位约束（仅加法）
                    if ensure_no_carrying and op == "+":
                        # 个位相加不能进位
                        if (a % 10) + (b % 10) >= 10:
                            continue
                        # 十位相加不能进位
                        if (a // 10) + (b // 10) >= 10:
                            continue

                    result = a + b if op == "+" else a - b
                    if result_limit and result > result_limit:
                        continue
                    if min_result and result < min_result:
                        continue
                    if result_within_10 and result > 10:
                        continue
                    if result_within_20 and result > 20:
                        continue
                    if result_within_100 and result > 100:
                        continue

                    stem = f"{a}{op}{b}=[BLANK]"

                elif q_type == "simple_fill":
                    # 简单填空：5 + [BLANK] = 8  或  8 - [BLANK] = 3
                    op = random.choice(["+", "-"])
                    if op == "+":
                        a = random.randint(num_min, min(50, num_max))
                        missing = random.randint(num_min, min(50, num_max))
                        result = a + missing
                        if result_limit and result > result_limit:
                            continue
                        stem = f"{a}+[BLANK]={result}"
                    else:
                        result = random.randint(1, 50)
                        missing = random.randint(1, 50)
                        a = result + missing
                        if a > 100:
                            continue
                        stem = f"{a}-[BLANK]={result}"

                elif q_type == "consecutive_add":
                    # 连加：1+6+19=[BLANK]
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
                    stem = f"{a}+{b}+{c}=[BLANK]"

                elif q_type == "consecutive_subtract":
                    # 连减：a-b-c=[BLANK]
                    if result_within_10:
                        # 10 以内连减：确保 a-b-c 的结果在 0-10 范围内
                        # 简单策略：生成 a，然后生成 b 和 c 使得 b+c <= a
                        a = random.randint(num_min, num_max if num_max > 0 else 10)
                        # b 最大为 a - num_min（确保 c 至少有 num_min）
                        max_b_for_c = a - num_min
                        if max_b_for_c < num_min:
                            continue  # 无法生成有效的 b 和 c
                        b = random.randint(num_min, min(max_b_for_c, num_max if num_max > 0 else 10))
                        # c 最大为 a - b
                        max_c = a - b
                        if max_c < num_min:
                            continue  # 无法生成有效的 c
                        c = random.randint(num_min, max_c)
                    else:
                        c = random.randint(num_min, min(30, num_max))
                        b = random.randint(num_min, min(30, max(num_min, num_max - c)))
                        a = random.randint(max(b + c, 20), min(100, b + c + 50))

                    if ensure_positive and (a - b - c < 0):
                        continue
                    stem = f"{a}-{b}-{c}=[BLANK]"

                elif q_type == "mixed_operation":
                    # 加减混合：49-19+27=[BLANK]
                    # 根据 result_within_10 调整范围
                    if result_within_10:
                        # 10 以内加减混合
                        a = random.randint(num_min, min(10, num_max))
                        b = random.randint(num_min, min(5, max(num_min, 10 - a)))
                        c = random.randint(num_min, min(5, max(num_min, 10 - a - b)))
                        op1 = random.choice(["+", "-"])
                        op2 = random.choice(["+", "-"])

                        # 确保至少有一个加法和一个减法（混合）
                        if op1 == op2:
                            op1 = "-"
                            op2 = "+"
                    else:
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

                    stem = f"{a}{op1}{b}{op2}{c}=[BLANK]"

                elif q_type == "missing_operand":
                    # 减法填空：17 - [BLANK]= 2
                    result = random.randint(1, 50)
                    missing = random.randint(1, 50)
                    a = result + missing
                    if a > 100:
                        continue
                    stem = f"{a}-[BLANK]={result}"

                elif q_type == "compare_simple":
                    # 简单比较：a [BLANK] b
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    if ensure_different and a == b:
                        continue
                    stem = f"{a}[BLANK]{b}"

                elif q_type == "compare_with_result":
                    # 运算后比较（支持混合运算）：74-28+22[BLANK]75
                    op1 = random.choice(["+", "-"])
                    op2 = random.choice(["+", "-"])

                    # 根据 result_within_10 调整数字范围
                    if result_within_10:
                        # 10 以内运算：单个数字或简单两步运算
                        # 简化为单步运算比较：2+4○7
                        a = random.randint(num_min, min(10, num_max))
                        b = random.randint(num_min, min(10, num_max))
                        op = random.choice(op_values)

                        if op == "+":
                            result = a + b
                        else:
                            result = a - b
                            if ensure_positive and result < 0:
                                continue

                        if result > 10:
                            continue

                        compare_type = random.choice(["equal", "greater", "less"])
                        if compare_type == "equal":
                            compare_num = result
                        elif compare_type == "greater":
                            compare_num = result + random.randint(1, 3)
                        else:
                            compare_num = result - random.randint(1, 3)
                            if compare_num < 0:
                                compare_num = result + random.randint(1, 3)

                        stem = f"{a}{op}{b}[BLANK]{compare_num}"
                    else:
                        # 100 以内运算
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

                        stem = f"{a}{op1}{b}{op2}{c}[BLANK]{compare_num}"

                elif q_type == "compare_mixed_operation":
                    # 混合运算比较（确保有加有减）：74-28+22[BLANK]75
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

                    stem = f"{a}{op1}{b}{op2}{c}[BLANK]{compare_num}"

                else:
                    # 默认：简单加减法
                    a = random.randint(num_min, num_max)
                    b = random.randint(num_min, num_max)
                    op = random.choice(["+", "-"])
                    if ensure_positive and op == "-" and a < b:
                        continue
                    stem = f"{a}{op}{b}=[BLANK]"

                if stem in used_stems:
                    # 记录尝试过的组合
                    all_possible_attempts.add((q_type, stem))
                    continue

                used_stems.add(stem)
                generated = True
                break
            else:
                # 100 次尝试后仍未生成有效题目，允许重复
                allow_duplicate = True
                used_stems.clear()  # 清空已用题目，允许重复
                # 重新尝试生成
                for retry_attempt in range(max_attempts):
                    q_type = random.choice(question_complexity)
                    stem = ""
                    # 重新生成题目逻辑（简化版，直接调用生成逻辑）
                    # 这里复用上面的生成逻辑，只是不再检查重复
                    # 为简化代码，我们直接跳出并重新尝试外层循环
                    generated = False
                    break

            if not generated and allow_duplicate:
                # 如果允许重复，强制生成一道题（可能重复）
                # 重新尝试生成一道题，不检查重复
                force_attempts = 100
                for force_attempt in range(force_attempts):
                    q_type = random.choice(question_complexity)
                    stem = ""
                    success = False

                    if q_type == "simple":
                        op = random.choice(op_values)
                        if fixed_addend and op == "+":
                            op = "+"
                            if not isinstance(fixed_addend, list):
                                fixed_addend = [fixed_addend]
                            a = random.choice(fixed_addend)
                            b = random.randint(num_min, num_max)
                        elif fixed_subtractor and op == "-":
                            op = "-"
                            a = random.randint(num_min, num_max)
                            b = fixed_subtractor
                        else:
                            a = random.randint(num_min, num_max)
                            b = random.randint(num_min, num_max)

                        if ensure_positive and op == "-" and a < b:
                            continue
                        result = a + b if op == "+" else a - b
                        if result_limit and result > result_limit:
                            continue
                        if min_result and result < min_result:
                            continue
                        if result_within_10 and result > 10:
                            continue
                        if result_within_20 and result > 20:
                            continue
                        stem = f"{a}{op}{b}=[BLANK]"
                        success = True

                    elif q_type == "compare_simple":
                        # 简单比大小
                        a = random.randint(num_min, num_max)
                        b = random.randint(num_min, num_max)
                        if ensure_different and a == b:
                            continue
                        stem = f"{a}[BLANK]{b}"
                        success = True

                    elif q_type == "compare_with_result":
                        # 运算后比较
                        if result_within_10:
                            a = random.randint(num_min, min(10, num_max))
                            b = random.randint(num_min, min(10, num_max))
                            op = random.choice(op_values)
                            if op == "+":
                                result = a + b
                            else:
                                result = a - b
                                if ensure_positive and result < 0:
                                    continue
                            if result > 10:
                                continue
                            compare_num = random.randint(1, 10)
                            stem = f"{a}{op}{b}[BLANK]{compare_num}"
                            success = True
                        else:
                            a = random.randint(20, 80)
                            b = random.randint(10, 50)
                            c = random.randint(10, 50)
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
                            if result < 0:
                                continue
                            compare_num = random.randint(1, 100)
                            stem = f"{a}{op1}{b}{op2}{c}[BLANK]{compare_num}"
                            success = True

                    elif q_type == "consecutive_add":
                        a = random.randint(num_min, min(50, max(num_min, num_max - 20)))
                        b = random.randint(1, min(30, max(1, num_max - a - 1)))
                        c = random.randint(1, min(30, max(1, num_max - a - b)))
                        result = a + b + c
                        if result_within_10 and result > 10:
                            continue
                        stem = f"{a}+{b}+{c}=[BLANK]"
                        success = True

                    elif q_type == "consecutive_subtract":
                        a = random.randint(num_min, min(10, num_max if num_max > 0 else 10))
                        max_b_for_c = a - num_min
                        if max_b_for_c < num_min:
                            continue
                        b = random.randint(num_min, min(max_b_for_c, num_max if num_max > 0 else 10))
                        max_c = a - b
                        if max_c < num_min:
                            continue
                        c = random.randint(num_min, max_c)
                        stem = f"{a}-{b}-{c}=[BLANK]"
                        success = True

                    elif q_type == "mixed_operation":
                        if result_within_10:
                            a = random.randint(num_min, min(10, num_max))
                            b = random.randint(num_min, min(5, max(num_min, 10 - a)))
                            c = random.randint(num_min, min(5, max(num_min, 10 - a - b)))
                            op1 = random.choice(["+", "-"])
                            op2 = random.choice(["+", "-"])
                            if op1 == op2:
                                op1 = "-"
                                op2 = "+"
                        else:
                            a = random.randint(20, min(80, num_max if num_max >= 20 else 80))
                            b = random.randint(1, min(50, num_max))
                            c = random.randint(1, min(50, num_max))
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

                        if result < 0:
                            continue
                        stem = f"{a}{op1}{b}{op2}{c}=[BLANK]"
                        success = True

                    elif q_type == "missing_operand":
                        result = random.randint(1, 50)
                        missing = random.randint(1, 50)
                        a = result + missing
                        if a > 100:
                            continue
                        stem = f"{a}-[BLANK]={result}"
                        success = True

                    elif q_type == "simple_fill":
                        op = random.choice(["+", "-"])
                        if op == "+":
                            a = random.randint(num_min, min(50, num_max))
                            missing = random.randint(num_min, min(50, num_max))
                            result = a + missing
                            if result_limit and result > result_limit:
                                continue
                            stem = f"{a}+[BLANK]={result}"
                        else:
                            result = random.randint(1, 50)
                            missing = random.randint(1, 50)
                            a = result + missing
                            if a > 100:
                                continue
                            stem = f"{a}-[BLANK]={result}"
                        success = True

                    if success and stem:
                        break

                # 如果还是无法生成，使用当前配置的最小题目
                if not stem:
                    # 根据配置生成一个保底题目
                    if fixed_addend:
                        a = fixed_addend[0] if isinstance(fixed_addend, list) else fixed_addend
                        b = num_min
                        stem = f"{a}+{b}=[BLANK]"
                    elif fixed_subtractor:
                        a = max(num_min, fixed_subtractor)
                        stem = f"{a}-{fixed_subtractor}=[BLANK]"
                    elif "compare" in str(question_complexity):
                        stem = f"{num_min}[BLANK]{num_min + 1}"
                    else:
                        stem = f"{num_min}+{num_min}=[BLANK]"

            # 应用 q_type 级别的 answer_style 配置（优先级高于 rendering_config）
            question_rendering_meta = rendering_meta.copy()
            if q_type in q_type_styles:
                question_rendering_meta["answer_style"] = q_type_styles[q_type]

            questions.append({
                "type": question_type,
                "stem": stem,
                "knowledge_points": self.get_knowledge_points(template_config),
                "rows_to_answer": 3,
                "rendering_meta": question_rendering_meta,
            })

        return questions

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        points = ["百以内加减法"]

        # 根据配置添加细分知识点
        if template_config.get("ensure_no_carrying", False):
            points.append("两位数加两位数（不进位）")
        if "consecutive_add" in template_config.get("question_complexity", []):
            points.append("连加")
        if "consecutive_subtract" in template_config.get("question_complexity", []):
            points.append("连减")
        if "mixed_operation" in template_config.get("question_complexity", []):
            points.append("加减混合运算")
        if "missing_operand" in template_config.get("question_complexity", []):
            points.append("逆向思维")
        if "compare_simple" in template_config.get("question_complexity", []):
            points.append("数的大小比较")

        return points
