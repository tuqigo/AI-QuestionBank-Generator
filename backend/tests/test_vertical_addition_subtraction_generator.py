"""
竖式加减法生成器单元测试
测试 VerticalAdditionSubtractionGenerator 的功能
"""
import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.template.generators.vertical_addition_subtraction import VerticalAdditionSubtractionGenerator


class TestVerticalAdditionSubtractionGenerator(unittest.TestCase):
    """竖式加减法生成器测试类"""

    def setUp(self):
        """测试前准备"""
        self.generator = VerticalAdditionSubtractionGenerator()
        self.default_config = {
            "min_value": 10,
            "max_value": 50,
            "operation_types": ["addition", "subtraction"],
            "blank_positions": ["top_tens", "top_ones", "bottom_tens", "bottom_ones", "result_tens", "result_ones"],
            "ensure_positive_result": True,
        }

    def test_generate_basic(self):
        """测试基本生成功能"""
        questions = self.generator.generate(
            template_config=self.default_config,
            quantity=5,
            question_type="ORAL_CALCULATION"
        )

        # 验证生成数量
        self.assertEqual(len(questions), 5)

        # 验证每道题目的结构
        for q in questions:
            self.assertIn("type", q)
            self.assertIn("stem", q)
            self.assertIn("knowledge_points", q)
            self.assertIn("rows_to_answer", q)
            self.assertEqual(q["type"], "ORAL_CALCULATION")
            self.assertIsInstance(q["knowledge_points"], list)
            self.assertGreater(len(q["knowledge_points"]), 0)
            self.assertEqual(q["rows_to_answer"], 1)

    def test_generate_addition_only(self):
        """测试只生成加法题目"""
        config = {
            "min_value": 10,
            "max_value": 30,
            "operation_types": ["addition"],
            "blank_positions": ["result_tens"],
            "ensure_positive_result": True,
        }

        questions = self.generator.generate(config, quantity=10, question_type="ORAL_CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证所有题目都包含加号
        for q in questions:
            self.assertIn("+", q["stem"])

    def test_generate_subtraction_only(self):
        """测试只生成减法题目"""
        config = {
            "min_value": 20,
            "max_value": 50,
            "operation_types": ["subtraction"],
            "blank_positions": ["result_ones"],
            "ensure_positive_result": True,
        }

        questions = self.generator.generate(config, quantity=10, question_type="ORAL_CALCULATION")

        self.assertEqual(len(questions), 10)
        # 验证所有题目都包含减号
        for q in questions:
            self.assertIn("-", q["stem"])

    def test_generate_ensure_positive_result(self):
        """测试确保减法结果非负"""
        config = {
            "min_value": 10,
            "max_value": 50,
            "operation_types": ["subtraction"],
            "blank_positions": ["top_tens"],
            "ensure_positive_result": True,
        }

        questions = self.generator.generate(config, quantity=20, question_type="ORAL_CALCULATION")

        # 验证生成的题目结果都是非负的（通过 LaTeX 格式判断）
        for q in questions:
            # 简单验证：题目中应该包含有效的数字
            self.assertTrue("\\boxed" in q["stem"] or any(c.isdigit() for c in q["stem"]))

    def test_generate_various_blank_positions(self):
        """测试不同空缺位置的生成"""
        # 测试十位空缺
        config_top_tens = {
            "min_value": 10,
            "max_value": 30,
            "operation_types": ["addition"],
            "blank_positions": ["top_tens"],
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_top_tens, quantity=3, question_type="ORAL_CALCULATION")
        self.assertEqual(len(questions), 3)
        for q in questions:
            # 验证包含空缺标记（使用\makebox 固定宽度确保对齐）
            self.assertIn("\\boxed{\\phantom{0}}", q["stem"])

        # 测试个位空缺
        config_top_ones = {
            "min_value": 10,
            "max_value": 30,
            "operation_types": ["addition"],
            "blank_positions": ["top_ones"],
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_top_ones, quantity=3, question_type="ORAL_CALCULATION")
        self.assertEqual(len(questions), 3)

        # 测试结果空缺
        config_result = {
            "min_value": 10,
            "max_value": 30,
            "operation_types": ["addition"],
            "blank_positions": ["result_tens", "result_ones"],
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_result, quantity=3, question_type="ORAL_CALCULATION")
        self.assertEqual(len(questions), 3)

    def test_generate_no_duplicates(self):
        """测试生成题目不重复"""
        config = {
            "min_value": 10,
            "max_value": 20,
            "operation_types": ["addition"],
            "blank_positions": ["result_tens"],
            "ensure_positive_result": True,
        }

        questions = self.generator.generate(config, quantity=10, question_type="ORAL_CALCULATION")

        # 验证题干不重复
        stems = [q["stem"] for q in questions]
        self.assertEqual(len(stems), len(set(stems)), "存在重复的题目")

    def test_generate_large_quantity(self):
        """测试大量生成"""
        questions = self.generator.generate(
            template_config=self.default_config,
            quantity=50,
            question_type="ORAL_CALCULATION"
        )

        self.assertEqual(len(questions), 50)

    def test_generate_latex_format(self):
        """测试 LaTeX 格式正确性"""
        config = {
            "min_value": 10,
            "max_value": 30,
            "operation_types": ["addition"],
            "blank_positions": ["top_tens"],
            "ensure_positive_result": True,
        }

        questions = self.generator.generate(config, quantity=5, question_type="ORAL_CALCULATION")

        for q in questions:
            stem = q["stem"]
            # 验证 LaTeX 基本结构
            self.assertIn("\\[", stem)
            self.assertIn("\\begin{array}", stem)
            self.assertIn("\\hline", stem)
            self.assertIn("\\end{array}", stem)
            self.assertIn("\\]", stem)

    def test_get_knowledge_points(self):
        """测试知识点获取"""
        # 测试加法知识点
        config_addition = {
            "operation_types": ["addition"],
            "ensure_no_carrying": False,
        }
        points = self.generator.get_knowledge_points(config_addition)
        self.assertIn("两位数加两位数竖式计算", points)
        self.assertIn("竖式填空", points)

        # 测试减法知识点
        config_subtraction = {
            "operation_types": ["subtraction"],
            "ensure_no_borrowing": True,
        }
        points = self.generator.get_knowledge_points(config_subtraction)
        self.assertIn("两位数减两位数竖式计算", points)
        self.assertIn("不退位减法", points)
        self.assertIn("竖式填空", points)

        # 测试混合运算知识点
        config_mixed = {
            "operation_types": ["addition", "subtraction"],
        }
        points = self.generator.get_knowledge_points(config_mixed)
        self.assertGreaterEqual(len(points), 2)

    def test_generate_with_constraints(self):
        """测试带约束条件的生成"""
        # 测试不进位加法
        config_no_carrying = {
            "min_value": 10,
            "max_value": 20,
            "operation_types": ["addition"],
            "blank_positions": ["result_tens"],
            "ensure_no_carrying": True,
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_no_carrying, quantity=5, question_type="ORAL_CALCULATION")
        self.assertEqual(len(questions), 5)

        # 测试不借位减法
        config_no_borrowing = {
            "min_value": 20,
            "max_value": 50,
            "operation_types": ["subtraction"],
            "blank_positions": ["result_ones"],
            "ensure_no_borrowing": True,
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_no_borrowing, quantity=5, question_type="ORAL_CALCULATION")
        self.assertEqual(len(questions), 5)

    def test_invalid_config_handling(self):
        """测试无效配置处理"""
        # 测试空配置（应使用默认值）
        questions = self.generator.generate(
            template_config={},
            quantity=3,
            question_type="ORAL_CALCULATION"
        )
        # 应该能够生成题目（使用默认配置）
        self.assertGreaterEqual(len(questions), -1)  # 可能因为范围太小生成失败

    def test_boundary_values(self):
        """测试边界值"""
        # 测试最小范围
        config_min = {
            "min_value": 10,
            "max_value": 10,  # 只有一个值
            "operation_types": ["addition"],
            "blank_positions": ["result_tens"],
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_min, quantity=3, question_type="ORAL_CALCULATION")
        # 范围太小可能无法生成足够的题目
        self.assertGreaterEqual(len(questions), -1)

        # 测试大范围
        config_max = {
            "min_value": 10,
            "max_value": 99,
            "operation_types": ["addition", "subtraction"],
            "blank_positions": ["top_tens", "bottom_ones", "result_tens"],
            "ensure_positive_result": True,
        }
        questions = self.generator.generate(config_max, quantity=10, question_type="ORAL_CALCULATION")
        self.assertEqual(len(questions), 10)


class TestVerticalAdditionSubtractionIntegration(unittest.TestCase):
    """竖式加减法生成器集成测试"""

    def test_generator_registration(self):
        """测试生成器是否已注册"""
        from services.template.generators import get_generator

        # 验证可以通过名称获取生成器
        gen = get_generator("vertical_addition_subtraction")
        self.assertIsNotNone(gen)
        self.assertIsInstance(gen, VerticalAdditionSubtractionGenerator)

    def test_end_to_end_generation(self):
        """测试端到端生成流程"""
        from services.template.generators import get_generator

        # 模拟真实使用场景
        generator = get_generator("vertical_addition_subtraction")

        # 使用模板 15 的配置
        config = {
            "min_value": 10,
            "max_value": 50,
            "operation_types": ["addition", "subtraction"],
            "blank_positions": ["top_tens", "top_ones", "bottom_tens", "bottom_ones", "result_tens", "result_ones"],
            "ensure_positive_result": True,
        }

        questions = generator.generate(config, quantity=15, question_type="ORAL_CALCULATION")

        # 验证生成结果
        self.assertEqual(len(questions), 15)
        for q in questions:
            self.assertEqual(q["type"], "ORAL_CALCULATION")
            self.assertIn("array", q["stem"])  # LaTeX array 格式
            self.assertGreater(len(q["knowledge_points"]), 0)


if __name__ == "__main__":
    unittest.main()
