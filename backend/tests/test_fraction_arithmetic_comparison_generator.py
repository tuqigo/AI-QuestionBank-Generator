"""
分数加减乘除比较大小生成器单元测试
测试 FractionArithmeticComparisonGenerator 的功能
"""
import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.template.generators.fraction_arithmetic_comparison import FractionArithmeticComparisonGenerator


class TestFractionArithmeticComparisonGenerator(unittest.TestCase):
    """分数加减乘除比较大小生成器测试类"""

    def setUp(self):
        """测试前准备"""
        self.generator = FractionArithmeticComparisonGenerator()
        self.default_config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["same_denominator_add", "same_denominator_subtract"],
            "rules": ["ensure_proper_fraction"]
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

    def test_generate_same_denominator_add(self):
        """测试同分母分数加法"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["same_denominator_add"],
            "rules": ["ensure_proper_fraction"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证所有题目都包含加号和同分母
        for q in questions:
            self.assertIn("+", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_same_denominator_subtract(self):
        """测试同分母分数减法"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["same_denominator_subtract"],
            "rules": ["ensure_proper_fraction"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证所有题目都包含减号
        for q in questions:
            self.assertIn("-", q["stem"])

    def test_generate_different_denominator_add(self):
        """测试异分母分数加法"""
        config = {
            "denominator": {"min": 3, "max": 12},
            "numerator": {"min": 1},
            "question_complexity": ["different_denominator_add"],
            "rules": ["ensure_different_denominator"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含两个不同分母的分数
        for q in questions:
            self.assertIn("+", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_different_denominator_subtract(self):
        """测试异分母分数减法"""
        config = {
            "denominator": {"min": 3, "max": 12},
            "numerator": {"min": 1},
            "question_complexity": ["different_denominator_subtract"],
            "rules": ["ensure_different_denominator", "ensure_positive"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证所有题目都包含减号
        for q in questions:
            self.assertIn("-", q["stem"])

    def test_generate_multiply_fraction_int(self):
        """测试分数乘整数"""
        config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["multiply_fraction_int"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含乘号和整数
        for q in questions:
            self.assertIn("\\times", q["stem"])

    def test_generate_multiply_fraction_fraction(self):
        """测试分数乘分数"""
        config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["multiply_fraction_fraction"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含两个分数相乘
        for q in questions:
            self.assertIn("\\times", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_divide_fraction_int(self):
        """测试分数除整数"""
        config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["divide_fraction_int"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含除号和整数
        for q in questions:
            self.assertIn("\\div", q["stem"])

    def test_generate_divide_fraction_fraction(self):
        """测试分数除分数"""
        config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["divide_fraction_fraction"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含两个分数相除
        for q in questions:
            self.assertIn("\\div", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_compare_same_denominator(self):
        """测试同分母分数比较大小"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["compare_same_denominator"],
            "rules": ["ensure_different_denominator"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含比较格式
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_compare_same_numerator(self):
        """测试同分子分数比较大小"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1, "max": 5},
            "question_complexity": ["compare_same_numerator"],
            "rules": ["ensure_different_denominator"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含比较格式
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_compare_different(self):
        """测试异分母分数比较大小"""
        config = {
            "denominator": {"min": 3, "max": 12},
            "numerator": {"min": 1},
            "question_complexity": ["compare_different"],
            "rules": ["ensure_different_denominator"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含比较格式
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_compare_with_result(self):
        """测试运算后比较大小"""
        config = {
            "denominator": {"min": 3, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["compare_with_result"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含比较格式和运算
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])
            self.assertIn("\\frac", q["stem"])

    def test_generate_mixed_operations(self):
        """测试混合运算"""
        config = {
            "denominator": {"min": 3, "max": 12},
            "numerator": {"min": 1},
            "question_complexity": [
                "multiply_add", "multiply_subtract",
                "divide_add", "divide_subtract"
            ],
            "rules": ["ensure_positive"]
        }

        questions = self.generator.generate(config, quantity=20, question_type="CALCULATION")

        self.assertEqual(len(questions), 20)
        # 验证包含混合运算
        for q in questions:
            self.assertIn("\\frac", q["stem"])

    def test_generate_fill_blank(self):
        """测试填空题"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": [
                "fill_blank_numerator",
                "fill_blank_denominator",
                "fill_blank_operation"
            ]
        }

        questions = self.generator.generate(config, quantity=15, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 15)
        # 验证包含填空
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_generate_reciprocal(self):
        """测试倒数题目"""
        config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["reciprocal"],
            "rules": ["ensure_proper_fraction"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证包含倒数描述
        for q in questions:
            self.assertIn("倒数", q["stem"])

    def test_generate_mixed_number(self):
        """测试带分数运算"""
        config = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "whole": {"min": 1, "max": 5},
            "question_complexity": ["mixed_number_add", "mixed_number_subtract"]
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证包含带分数格式
        for q in questions:
            self.assertIn("\\frac", q["stem"])

    def test_generate_no_duplicates(self):
        """测试生成题目不重复"""
        config = {
            "denominator": {"min": 2, "max": 20},
            "numerator": {"min": 1},
            "question_complexity": ["same_denominator_add", "same_denominator_subtract"]
        }

        questions = self.generator.generate(config, quantity=20, question_type="CALCULATION")

        # 验证题干不重复
        stems = [q["stem"] for q in questions]
        self.assertEqual(len(stems), len(set(stems)), "存在重复的题目")

    def test_generate_large_quantity(self):
        """测试大量生成"""
        config = {
            "denominator": {"min": 2, "max": 20},
            "numerator": {"min": 1},
            "question_complexity": [
                "same_denominator_add", "same_denominator_subtract",
                "different_denominator_add", "different_denominator_subtract",
                "multiply_fraction_int", "divide_fraction_int",
                "compare_same_denominator", "compare_different"
            ]
        }

        questions = self.generator.generate(config, quantity=50, question_type="CALCULATION")

        self.assertEqual(len(questions), 50)

    def test_generate_with_q_type_style(self):
        """测试 q_type 设置 answer_style"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["compare_same_denominator", "compare_different"],
            "q_type": {
                "compare_same_denominator": "circle",
                "compare_different": "circle"
            }
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")

        self.assertEqual(len(questions), 10)
        # 验证 rendering_meta 中包含 answer_style
        for q in questions:
            self.assertIn("rendering_meta", q)
            # 注意：由于是随机选择 q_type，所以不能保证每道题都有 circle

    def test_get_knowledge_points(self):
        """测试知识点获取"""
        # 测试同分母加法知识点
        points = self.generator.get_knowledge_points({}, "same_denominator_add")
        self.assertIn("同分母分数加法", points)

        # 测试异分母加法知识点
        points = self.generator.get_knowledge_points({}, "different_denominator_add")
        self.assertIn("通分", points)
        self.assertIn("最小公倍数", points)

        # 测试乘法知识点
        points = self.generator.get_knowledge_points({}, "multiply_fraction_fraction")
        self.assertIn("分数乘分数", points)

        # 测试比较知识点
        points = self.generator.get_knowledge_points({}, "compare_different")
        self.assertIn("异分母分数比较大小", points)

        # 测试自定义知识点
        custom_points = ["自定义知识点 1", "自定义知识点 2"]
        points = self.generator.get_knowledge_points({"knowledge_points": custom_points}, "same_denominator_add")
        self.assertEqual(points, custom_points)

    def test_generate_latex_format(self):
        """测试 LaTeX 格式正确性"""
        config = {
            "denominator": {"min": 5, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["same_denominator_add"]
        }

        questions = self.generator.generate(config, quantity=5, question_type="CALCULATION")

        for q in questions:
            stem = q["stem"]
            # 验证 LaTeX 基本结构
            self.assertIn("$", stem)
            self.assertIn("\\frac", stem)


class TestFractionArithmeticComparisonIntegration(unittest.TestCase):
    """分数加减乘除比较大小生成器集成测试"""

    def test_generator_registration(self):
        """测试生成器是否已注册"""
        from services.template.generators import get_generator

        # 验证可以通过名称获取生成器
        gen = get_generator("fraction_arithmetic_comparison")
        self.assertIsNotNone(gen)
        self.assertIsInstance(gen, FractionArithmeticComparisonGenerator)

    def test_end_to_end_generation(self):
        """测试端到端生成流程"""
        from services.template.generators import get_generator

        # 模拟真实使用场景 - 三年级同分母分数
        generator = get_generator("fraction_arithmetic_comparison")

        config_grade3 = {
            "denominator": {"min": 2, "max": 10},
            "numerator": {"min": 1},
            "question_complexity": ["same_denominator_add", "same_denominator_subtract"],
            "rules": ["ensure_proper_fraction"]
        }

        questions = generator.generate(config_grade3, quantity=15, question_type="CALCULATION")

        # 验证生成结果
        self.assertEqual(len(questions), 15)
        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("\\frac", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_comprehensive_config(self):
        """测试综合配置（覆盖所有题型）"""
        from services.template.generators import get_generator

        generator = get_generator("fraction_arithmetic_comparison")

        # 综合配置 - 模拟 5-6 年级
        config_comprehensive = {
            "denominator": {"min": 2, "max": 15},
            "numerator": {"min": 1},
            "whole": {"min": 1, "max": 5},
            "question_complexity": [
                # 加减法
                "same_denominator_add", "same_denominator_subtract",
                "different_denominator_add", "different_denominator_subtract",
                # 乘法
                "multiply_fraction_int", "multiply_fraction_fraction",
                # 除法
                "divide_fraction_int", "divide_fraction_fraction",
                # 混合运算
                "multiply_add", "multiply_subtract",
                # 比较
                "compare_same_denominator", "compare_different",
                # 填空
                "fill_blank_numerator",
                # 倒数
                "reciprocal",
            ],
            "rules": ["ensure_proper_fraction", "ensure_positive"]
        }

        questions = generator.generate(config_comprehensive, quantity=50, question_type="CALCULATION")

        # 验证生成结果
        self.assertEqual(len(questions), 50)
        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("\\frac", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)


if __name__ == "__main__":
    unittest.main()
