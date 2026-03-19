"""
模板：竖式加减法（两位数加减两位数，竖式填空）
生成逻辑：生成竖式形式的加减法题目，个位或十位留空需要学生填写
例题：
  [ \begin{array}{r} \ \ \ \boxed{\phantom{0}}\ 6 \\[4pt] + \ \ 2\ \boxed{\phantom{0}} \\[4pt] \hline \ \ \ 4\ \ \ 5 \end{array} ]
  [ \begin{array}{r} \ \ \ 5\ \boxed{\phantom{0}} \\[4pt] - \ \ \boxed{\phantom{0}}\ 4 \\[4pt] \hline \ \ \ 2\ \ \ 5 \end{array} ]
"""
import random
from typing import List, Dict, Any

from .base import TemplateGenerator


class VerticalAdditionSubtractionGenerator(TemplateGenerator):
    """竖式加减法生成器（两位数加减两位数，竖式填空）"""

    def generate(self, template_config: dict, quantity: int, question_type: str) -> List[Dict[str, Any]]:
        questions = []
        used_stems = set()

        # 读取配置参数
        min_value = template_config.get("min_value", 10)  # 最小两位数
        max_value = template_config.get("max_value", 99)  # 最大两位数
        operation_types = template_config.get("operation_types", ["addition", "subtraction"])  # 运算类型
        # 空缺位置类型：top_tens, top_ones, bottom_tens, bottom_ones, result_tens, result_ones
        blank_positions = template_config.get("blank_positions", ["top_tens", "top_ones", "bottom_tens", "bottom_ones"])
        ensure_no_borrowing = template_config.get("ensure_no_borrowing", False)  # 减法不借位
        ensure_no_carrying = template_config.get("ensure_no_carrying", False)  # 加法不进位
        ensure_positive_result = template_config.get("ensure_positive_result", True)  # 确保结果非负

        for _ in range(quantity):
            max_attempts = 50
            for attempt in range(max_attempts):
                # 随机选择运算类型
                operation = random.choice(operation_types)

                # 生成两个两位数
                num1 = random.randint(min_value, max_value)  # 被加数/被减数
                num2 = random.randint(min_value, max_value)  # 加数/减数

                # 检查运算合法性
                if operation == "subtraction" and ensure_positive_result:
                    if num1 < num2:
                        continue  # 确保结果非负

                # 检查进位/借位约束
                if operation == "addition" and ensure_no_carrying:
                    # 检查个位相加是否进位
                    if (num1 % 10) + (num2 % 10) >= 10:
                        continue
                    # 检查十位相加是否进位
                    if (num1 // 10) + (num2 // 10) >= 10:
                        continue

                if operation == "subtraction" and ensure_no_borrowing:
                    # 检查个位是否需要借位
                    if (num1 % 10) < (num2 % 10):
                        continue
                    # 检查十位是否需要借位
                    if (num1 // 10) < (num2 // 10):
                        continue

                # 计算结果
                result = num1 + num2 if operation == "addition" else num1 - num2

                # 随机选择空缺位置
                blank_pos = random.choice(blank_positions)

                # 生成竖式 LaTeX 格式
                stem = self._generate_vertical_latex(num1, num2, result, operation, blank_pos)

                # 检查是否重复
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

    def _generate_vertical_latex(self, num1: int, num2: int, result: int, operation: str, blank_pos: str) -> str:
        """
        生成竖式 LaTeX 格式

        Args:
            num1: 第一个数（被加数/被减数）
            num2: 第二个数（加数/减数）
            result: 结果
            operation: 运算类型 (addition/subtraction)
            blank_pos: 空缺位置

        Returns:
            LaTeX 格式的竖式字符串
        """
        # 分解数字
        num1_tens = num1 // 10
        num1_ones = num1 % 10
        num2_tens = num2 // 10
        num2_ones = num2 % 10
        result_tens = result // 10
        result_ones = result % 10

        op_symbol = "+" if operation == "addition" else "-"

        # 根据空缺位置生成填空
        if blank_pos == "top_tens":
            num1_str = f"\\boxed{{\\phantom{{0}}}} {num1_ones}"
        elif blank_pos == "top_ones":
            num1_str = f" {num1_tens}\\boxed{{\\phantom{{0}}}}"
        elif blank_pos == "bottom_tens":
            num2_str = f"\\boxed{{\\phantom{{0}}}} {num2_ones}"
        elif blank_pos == "bottom_ones":
            num2_str = f" {num2_tens}\\boxed{{\\phantom{{0}}}}"
        elif blank_pos == "result_tens":
            result_str = f"\\boxed{{\\phantom{{0}}}} {result_ones}"
        elif blank_pos == "result_ones":
            result_str = f" {result_tens}\\boxed{{\\phantom{{0}}}}"
        else:
            # 默认无空缺
            num1_str = f" {num1_tens} {num1_ones}"
            num2_str = f" {num2_tens} {num2_ones}"
            result_str = f" {result_tens} {result_ones}"

        # 确保变量已定义（如果空缺在 num1 或 num2）
        if 'num1_str' not in dir():
            num1_str = f" {num1_tens} {num1_ones}"
        if 'num2_str' not in dir():
            num2_str = f" {num2_tens} {num2_ones}"
        if 'result_str' not in dir():
            result_str = f" {result_tens} {result_ones}"

        # 生成 LaTeX 竖式
        latex = f"""\\[ \\begin{{array}}{{r}}
  {num1_str} \\\\[4pt]
{op_symbol} {num2_str} \\\\[4pt]
\\hline
  {result_str}
\\end{{array}} \\]"""

        return latex

    def get_knowledge_points(self, template_config: dict) -> List[str]:
        """获取知识点列表"""
        operation_types = template_config.get("operation_types", ["addition", "subtraction"])

        points = []
        if "addition" in operation_types:
            points.append("两位数加两位数竖式计算")
        if "subtraction" in operation_types:
            points.append("两位数减两位数竖式计算")

        # 根据配置添加额外知识点
        if template_config.get("ensure_no_borrowing", False):
            points.append("不退位减法")
        if template_config.get("ensure_no_carrying", False):
            points.append("不进位加法")

        points.append("竖式填空")

        return points
