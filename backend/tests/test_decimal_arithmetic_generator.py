"""
小数乘除法综合生成器单元测试
测试 DecimalArithmeticGenerator 的功能
"""
import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.template.generators.decimal_arithmetic import DecimalArithmeticGenerator


class TestDecimalArithmeticGenerator(unittest.TestCase):
    """小数乘除法综合生成器测试类"""

    def setUp(self):
        """测试前准备"""
        self.generator = DecimalArithmeticGenerator()
        self.default_config = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 10},
            "question_complexity": ["multiply_decimal_int"],
            "rules": ["result_two_decimal_places"]
        }

    def test_generate_basic(self):
        """测试基本生成功能"""
        questions = self.generator.generate(
            template_config=self.default_config,
            quantity=5,
            question_type="CALCULATION"
        )

        # 验证生成数量
        self.assertEqual(len(questions), 5)

        # 验证每道题目的结构
        for q in questions:
            self.assertIn("type", q)
            self.assertIn("stem", q)
            self.assertIn("knowledge_points", q)
            self.assertIn("rows_to_answer", q)
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIsInstance(q["knowledge_points"], list)
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_generate_multiply_decimal_int(self):
        """测试小数乘整数"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 10},
            "question_complexity": ["multiply_decimal_int"],
            "rules": ["result_two_decimal_places"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证所有题目都包含乘号和整数
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_multiply_decimal_decimal(self):
        """测试小数乘小数"""
        config = {
            "decimal_places_factor1": {"min": 1, "max": 2},
            "decimal_places_factor2": {"min": 1, "max": 1},
            "question_complexity": ["multiply_decimal_decimal"],
            "rules": ["result_two_decimal_places"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含两个小数相乘
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_multiply_commutative(self):
        """测试乘法交换律"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 10},
            "question_complexity": ["multiply_commutative"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证交换律格式
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_multiply_associative(self):
        """测试乘法结合律"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["multiply_associative"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证结合律格式（包含括号）
        for q in questions:
            self.assertIn("(", q["stem"])
            self.assertIn("\\times", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_multiply_distributive(self):
        """测试乘法分配律"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["multiply_distributive"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证分配律格式
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("+", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_multiply_distributive_fill(self):
        """测试乘法分配律填空"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["multiply_distributive_fill"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证分配律填空格式（逆向应用）
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("+", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_divide_decimal_int(self):
        """测试小数除以整数"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "divisor_range": {"min": 2, "max": 10},
            "question_complexity": ["divide_decimal_int"],
            "rules": ["no_remainder"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含除号
        for q in questions:
            self.assertIn("\\div", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_divide_decimal_int_with_remainder(self):
        """测试小数除以整数（有余数）"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["divide_decimal_int_with_remainder"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        for q in questions:
            self.assertIn("\\div", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_divide_int_decimal(self):
        """测试整数除以小数"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["divide_int_decimal"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        for q in questions:
            self.assertIn("\\div", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_divide_decimal_decimal(self):
        """测试小数除以小数"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["divide_decimal_decimal"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        for q in questions:
            self.assertIn("\\div", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_approximate_quotient(self):
        """测试商的近似值"""
        config = {
            "dividend_range": {"min": 10, "max": 100},
            "divisor_range": {"min": 3, "max": 20},
            "question_complexity": ["approximate_quotient"],
            "approximate_places": 2,
            "approximate_method": "half_up"
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含约等号和保留位数说明
        for q in questions:
            self.assertIn("\\approx", q["stem"])
            self.assertIn("保留", q["stem"])

    def test_generate_repeating_decimal_identify(self):
        """测试循环小数识别"""
        config = {
            "question_complexity": ["repeating_decimal_identify"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含循环小数标记
        for q in questions:
            self.assertIn("\\dot", q["stem"])

    def test_generate_repeating_decimal_write(self):
        """测试用循环小数表示商"""
        config = {
            "question_complexity": ["repeating_decimal_write"]
        }

        questions = self.generator.generate(config, quantity=8, question_type="CALCULATION")

        self.assertEqual(len(questions), 8)
        # 验证包含循环小数说明
        for q in questions:
            self.assertIn("循环小数", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_mixed_operations(self):
        """测试小数乘除混合运算"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": [
                "multiply_divide_mixed",
                "multiply_multiply"
            ]
        }

        questions = self.generator.generate(config, quantity=20, question_type="CALCULATION")

        self.assertEqual(len(questions), 20)
        # 验证包含混合运算
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_compare_size(self):
        """测试小数比较大小"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": [
                "compare_multiply_result",
                "compare_divide_result"
            ]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含比较格式
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_fill_blank(self):
        """测试小数填空"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": [
                "fill_missing_factor",
                "fill_divisor"
            ]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含填空
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_no_duplicates(self):
        """测试生成题目不重复"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 20},
            "question_complexity": [
                "multiply_decimal_int",
                "multiply_decimal_decimal",
                "divide_decimal_int"
            ]
        }

        questions = self.generator.generate(config, quantity=20, question_type="CALCULATION")

        # 验证题干不重复
        stems = [q["stem"] for q in questions]
        self.assertEqual(len(stems), len(set(stems)), "存在重复的题目")

    def test_generate_large_quantity(self):
        """测试大量生成"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 20},
            "question_complexity": [
                "multiply_decimal_int",
                "multiply_decimal_decimal",
                "multiply_commutative",
                "multiply_associative",
                "divide_decimal_int",
                "divide_decimal_decimal",
                "approximate_quotient",
                "compare_multiply_result"
            ]
        }

        questions = self.generator.generate(config, quantity=50, question_type="CALCULATION")

        self.assertEqual(len(questions), 50)

    def test_generate_with_q_type_style(self):
        """测试 q_type 设置 answer_style"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["compare_multiply_result", "compare_divide_result"],
            "q_type": {
                "compare_multiply_result": "circle",
                "compare_divide_result": "circle"
            }
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证 rendering_meta 中包含 answer_style
        for q in questions:
            self.assertIn("rendering_meta", q)

    def test_get_knowledge_points(self):
        """测试知识点获取"""
        # 测试小数乘整数知识点
        points = self.generator.get_knowledge_points({}, "multiply_decimal_int")
        self.assertIn("小数乘整数", points)

        # 测试小数乘小数知识点
        points = self.generator.get_knowledge_points({}, "multiply_decimal_decimal")
        self.assertIn("小数乘小数", points)

        # 测试乘法交换律知识点
        points = self.generator.get_knowledge_points({}, "multiply_commutative")
        self.assertIn("乘法交换律", points)

        # 测试乘法分配律知识点
        points = self.generator.get_knowledge_points({}, "multiply_distributive")
        self.assertIn("乘法分配律", points)

        # 测试小数除法知识点
        points = self.generator.get_knowledge_points({}, "divide_decimal_int")
        self.assertIn("小数除以整数", points)

        # 测试商的近似值知识点
        points = self.generator.get_knowledge_points({}, "approximate_quotient")
        self.assertIn("商的近似值", points)

        # 测试循环小数知识点
        points = self.generator.get_knowledge_points({}, "repeating_decimal_identify")
        self.assertIn("循环小数的认识", points)

        # 测试自定义知识点
        custom_points = ["自定义知识点 1", "自定义知识点 2"]
        points = self.generator.get_knowledge_points({"knowledge_points": custom_points}, "multiply_decimal_int")
        self.assertEqual(points, custom_points)

    def test_generate_latex_format(self):
        """测试 LaTeX 格式正确性"""
        config = {
            "decimal_places": {"min": 1, "max": 2},
            "question_complexity": ["multiply_decimal_int"]
        }

        questions = self.generator.generate(config, quantity=5, question_type="CALCULATION")

        for q in questions:
            stem = q["stem"]
            # 验证 LaTeX 基本结构
            self.assertIn("$", stem)
            self.assertIn("\\times", stem)

    def test_round_decimal_helper(self):
        """测试小数舍入辅助函数"""
        from services.template.generators.decimal_arithmetic import round_decimal

        # 测试四舍五入
        result = round_decimal(3.14159, 2, "half_up")
        self.assertEqual(result, 3.14)

        # 测试保留 1 位小数
        result = round_decimal(3.14159, 1, "half_up")
        self.assertEqual(result, 3.1)

    def test_format_decimal_helper(self):
        """测试小数格式化辅助函数"""
        from services.template.generators.decimal_arithmetic import format_decimal

        # 测试去除末尾 0
        result = format_decimal(3.50)
        self.assertEqual(result, "3.5")

        # 测试整数
        result = format_decimal(5.0)
        self.assertEqual(result, "5")


class TestDecimalArithmeticIntegration(unittest.TestCase):
    """小数乘除法综合生成器集成测试"""

    def test_generator_registration(self):
        """测试生成器是否已注册"""
        from services.template.generators import get_generator

        # 验证可以通过名称获取生成器
        gen = get_generator("decimal_arithmetic")
        self.assertIsNotNone(gen)
        self.assertIsInstance(gen, DecimalArithmeticGenerator)

    def test_end_to_end_generation_grade3(self):
        """测试端到端生成流程 - 三年级（小数初步认识）"""
        from services.template.generators import get_generator

        generator = get_generator("decimal_arithmetic")

        # 三年级配置 - 简单的小数乘整数
        config_grade3 = {
            "decimal_places": {"min": 1, "max": 1},
            "factor_int": {"min": 2, "max": 5},
            "question_complexity": ["multiply_decimal_int"],
            "rules": ["result_one_decimal_places"]
        }

        questions = generator.generate(config_grade3, quantity=10, question_type="CALCULATION")

        # 验证生成结果
        self.assertEqual(len(questions), 10)
        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("\\times", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_end_to_end_generation_grade5(self):
        """测试端到端生成流程 - 五年级（小数乘除法）"""
        from services.template.generators import get_generator

        generator = get_generator("decimal_arithmetic")

        # 五年级配置 - 综合乘除法
        config_grade5 = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 10},
            "dividend_range": {"min": 10, "max": 100},
            "divisor_range": {"min": 2, "max": 20},
            "question_complexity": [
                "multiply_decimal_int",
                "multiply_decimal_decimal",
                "divide_decimal_int",
                "divide_decimal_decimal",
                "approximate_quotient"
            ],
            "rules": ["result_two_decimal_places"]
        }

        questions = generator.generate(config_grade5, quantity=30, question_type="CALCULATION")

        # 验证生成结果
        self.assertEqual(len(questions), 30)
        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("$", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_comprehensive_config(self):
        """测试综合配置（覆盖所有题型）"""
        from services.template.generators import get_generator

        generator = get_generator("decimal_arithmetic")

        # 综合配置 - 模拟 5-6 年级综合练习
        config_comprehensive = {
            "decimal_places": {"min": 1, "max": 2},
            "factor_int": {"min": 2, "max": 10},
            "dividend_range": {"min": 10, "max": 100},
            "divisor_range": {"min": 2, "max": 20},
            "approximate_places": 2,
            "question_complexity": [
                # 乘法
                "multiply_decimal_int",
                "multiply_decimal_decimal",
                "multiply_commutative",
                "multiply_associative",
                "multiply_distributive",
                # 除法
                "divide_decimal_int",
                "divide_int_decimal",
                "divide_decimal_decimal",
                # 近似值
                "approximate_quotient",
                # 循环小数
                "repeating_decimal_identify",
                "repeating_decimal_write",
                # 混合运算
                "multiply_divide_mixed",
                # 比较
                "compare_multiply_result",
                "compare_divide_result",
                # 填空
                "fill_missing_factor",
                "fill_divisor"
            ],
            "rules": ["result_two_decimal_places"]
        }

        questions = generator.generate(config_comprehensive, quantity=50, question_type="CALCULATION")

        # 验证生成结果
        self.assertEqual(len(questions), 50)
        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("$", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)


if __name__ == "__main__":
    unittest.main()
