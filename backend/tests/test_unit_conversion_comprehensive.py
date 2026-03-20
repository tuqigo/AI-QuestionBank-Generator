"""
小学单位换算综合生成器单元测试
测试 UnitConversionComprehensiveGenerator 的功能
"""
import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.template.generators.unit_conversion_comprehensive import UnitConversionComprehensiveGenerator


class TestUnitConversionComprehensiveGenerator(unittest.TestCase):
    """小学单位换算综合生成器测试类"""

    def setUp(self):
        """测试前准备"""
        self.generator = UnitConversionComprehensiveGenerator()

    # ==================== 人民币换算测试 ====================
    def test_currency_grade1(self):
        """测试一年级人民币换算"""
        config = {
            "unit_category": "currency",
            "grade_level": "grade1",
            "convert_types": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao"],
            "value_range": {"min": 1, "max": 10}
        }

        questions = self.generator.generate(config, quantity=15, question_type="CALCULATION")
        self.assertEqual(len(questions), 15)

        # 验证题目格式（包含元或角或分）
        for q in questions:
            self.assertTrue("元" in q["stem"] or "角" in q["stem"] or "分" in q["stem"])
            self.assertIn("[BLANK]", q["stem"])

    def test_currency_yuan_to_jiao(self):
        """测试元化角"""
        config = {
            "unit_category": "currency",
            "convert_types": ["yuan_to_jiao"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("元 = [BLANK]角", q["stem"])

    def test_currency_jiao_to_yuan(self):
        """测试角化元"""
        config = {
            "unit_category": "currency",
            "convert_types": ["jiao_to_yuan"],
            "value_range": {"min": 10, "max": 100}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("角 = [BLANK]元", q["stem"])

    def test_currency_compound(self):
        """测试复名数换算"""
        config = {
            "unit_category": "currency",
            "convert_types": ["yuan_jiao_to_jiao", "yuan_fen_to_fen", "yuan_jiao_fen_to_fen"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=15, question_type="CALCULATION")
        self.assertEqual(len(questions), 15)

        # 验证包含复名数格式
        has_compound = any("元" in q["stem"] and ("角" in q["stem"] or "分" in q["stem"]) for q in questions)
        self.assertTrue(has_compound, "应该包含复名数题目")

    # ==================== 长度换算测试 ====================
    def test_length_grade1(self):
        """测试一年级长度单位"""
        config = {
            "unit_category": "length",
            "grade_level": "grade1",
            "convert_types": ["m_to_cm", "cm_to_m"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

    def test_length_m_to_cm(self):
        """测试米化厘米"""
        config = {
            "unit_category": "length",
            "convert_types": ["m_to_cm"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("m = [BLANK]cm", q["stem"])

    def test_length_km_to_m(self):
        """测试千米化米"""
        config = {
            "unit_category": "length",
            "convert_types": ["km_to_m"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("km = [BLANK]m", q["stem"])

    def test_length_compound(self):
        """测试长度复名数"""
        config = {
            "unit_category": "length",
            "convert_types": ["m_cm_to_cm", "m_dm_to_dm", "dm_cm_to_cm"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=15, question_type="CALCULATION")
        self.assertEqual(len(questions), 15)

    # ==================== 质量换算测试 ====================
    def test_mass_kg_to_g(self):
        """测试千克化克"""
        config = {
            "unit_category": "mass",
            "convert_types": ["kg_to_g"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("kg = [BLANK]g", q["stem"])

    def test_mass_t_to_kg(self):
        """测试吨化千克"""
        config = {
            "unit_category": "mass",
            "convert_types": ["t_to_kg"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("t = [BLANK]kg", q["stem"])

    def test_mass_compound(self):
        """测试质量复名数"""
        config = {
            "unit_category": "mass",
            "convert_types": ["kg_g_to_g", "t_kg_to_kg"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

    # ==================== 面积换算测试 ====================
    def test_area_m2_to_dm2(self):
        """测试平方米化平方分米"""
        config = {
            "unit_category": "area",
            "convert_types": ["m2_to_dm2"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("m² = [BLANK]dm²", q["stem"])

    def test_area_hectare(self):
        """测试公顷换算"""
        config = {
            "unit_category": "area",
            "convert_types": ["hectare_to_m2", "m2_to_hectare", "km2_to_hectare"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=15, question_type="CALCULATION")
        self.assertEqual(len(questions), 15)

    # ==================== 体积/容积换算测试 ====================
    def test_volume_m3_to_dm3(self):
        """测试立方米化立方分米"""
        config = {
            "unit_category": "volume",
            "convert_types": ["m3_to_dm3"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("m³ = [BLANK]dm³", q["stem"])

    def test_volume_l_to_ml(self):
        """测试升化毫升"""
        config = {
            "unit_category": "volume",
            "convert_types": ["l_to_ml"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("L = [BLANK]mL", q["stem"])

    def test_volume_dm3_to_l(self):
        """测试立方分米化升"""
        config = {
            "unit_category": "volume",
            "convert_types": ["dm3_to_l", "l_to_dm3"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

    # ==================== 时间换算测试 ====================
    def test_time_hour_minute(self):
        """测试时分化秒"""
        config = {
            "unit_category": "time",
            "convert_types": ["hour_to_minute", "minute_to_hour"],
            "value_range": {"min": 1, "max": 12}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

    def test_time_year_month(self):
        """测试年月换算"""
        config = {
            "unit_category": "time",
            "convert_types": ["year_to_month", "month_to_year"],
            "value_range": {"min": 1, "max": 10}
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

    def test_time_compound(self):
        """测试时间复名数"""
        config = {
            "unit_category": "time",
            "convert_types": ["hour_minute_to_minute", "day_hour_to_hour", "year_month_to_month"],
            "value_range": {"min": 1, "max": 10}
        }

        questions = self.generator.generate(config, quantity=15, question_type="CALCULATION")
        self.assertEqual(len(questions), 15)

    # ==================== 综合测试 ====================
    def test_no_duplicates(self):
        """测试生成题目不重复"""
        config = {
            "unit_category": "currency",
            "convert_types": ["yuan_to_jiao", "jiao_to_yuan", "yuan_jiao_to_jiao"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = self.generator.generate(config, quantity=30, question_type="CALCULATION")

        stems = [q["stem"] for q in questions]
        self.assertEqual(len(stems), len(set(stems)), "存在重复的题目")

    def test_large_quantity(self):
        """测试大量生成"""
        config = {
            "unit_category": "length",
            "convert_types": [
                "m_to_cm", "cm_to_m", "dm_to_cm", "cm_to_dm",
                "km_to_m", "m_to_km", "m_cm_to_cm"
            ],
            "value_range": {"min": 1, "max": 100}
        }

        questions = self.generator.generate(config, quantity=50, question_type="CALCULATION")
        self.assertEqual(len(questions), 50)

    def test_knowledge_points(self):
        """测试知识点获取"""
        # 测试人民币知识点
        points = self.generator.get_knowledge_points({}, "currency", "yuan_to_jiao")
        self.assertIn("认识人民币", points)
        self.assertIn("元化角", points)

        # 测试长度知识点
        points = self.generator.get_knowledge_points({}, "length", "m_to_cm")
        self.assertIn("长度单位的认识", points)

        # 测试质量知识点
        points = self.generator.get_knowledge_points({}, "mass", "kg_to_g")
        self.assertIn("质量单位的认识", points)

        # 测试面积知识点
        points = self.generator.get_knowledge_points({}, "area", "hectare_to_m2")
        self.assertIn("公顷和平方千米", points)

        # 测试体积知识点
        points = self.generator.get_knowledge_points({}, "volume", "l_to_ml")
        self.assertIn("体积单位的认识", points)

        # 测试时间知识点
        points = self.generator.get_knowledge_points({}, "time", "hour_to_minute")
        self.assertIn("时间单位的认识", points)

        # 测试自定义知识点
        custom_points = ["自定义知识点"]
        points = self.generator.get_knowledge_points({"knowledge_points": custom_points}, "currency")
        self.assertEqual(points, custom_points)

    def test_with_q_type_style(self):
        """测试 q_type 设置 answer_style"""
        config = {
            "unit_category": "currency",
            "convert_types": ["yuan_to_jiao", "jiao_to_yuan"],
            "q_type": {
                "yuan_to_jiao": "circle"
            }
        }

        questions = self.generator.generate(config, quantity=10, question_type="CALCULATION")
        self.assertEqual(len(questions), 10)

        # 验证 rendering_meta 存在
        for q in questions:
            self.assertIn("rendering_meta", q)

    # ==================== 比较大小测试 ====================
    def test_comparison_currency(self):
        """测试人民币比较大小"""
        config = {
            "unit_category": "currency",
            "convert_types": ["yuan_to_jiao", "jiao_to_fen"],
            "is_comparison": True,
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")
        self.assertEqual(len(questions), 10)

        # 验证包含比较格式
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])
            # 应该包含元或角或分
            self.assertTrue("元" in q["stem"] or "角" in q["stem"] or "分" in q["stem"])

    def test_comparison_length(self):
        """测试长度比较大小"""
        config = {
            "unit_category": "length",
            "convert_types": ["m_to_cm", "km_to_m"],
            "is_comparison": True,
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")
        self.assertEqual(len(questions), 10)

        # 验证包含比较格式
        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_comparison_mass(self):
        """测试质量比较大小"""
        config = {
            "unit_category": "mass",
            "convert_types": ["kg_to_g", "t_to_kg"],
            "is_comparison": True,
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_comparison_volume(self):
        """测试体积比较大小"""
        config = {
            "unit_category": "volume",
            "convert_types": ["m3_to_dm3", "l_to_ml"],
            "is_comparison": True,
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_comparison_time(self):
        """测试时间比较大小"""
        config = {
            "unit_category": "time",
            "convert_types": ["hour_to_minute", "year_to_month"],
            "is_comparison": True,
            "value_range": {"min": 1, "max": 10}
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")
        self.assertEqual(len(questions), 10)

        for q in questions:
            self.assertIn("[BLANK]", q["stem"])

    def test_comparison_with_circle_style(self):
        """测试比较大小题目使用圆圈作答样式"""
        config = {
            "unit_category": "currency",
            "convert_types": ["yuan_to_jiao"],
            "is_comparison": True,
            "q_type": {"compare_yuan_jiao": "circle"},
            "value_range": {"min": 1, "max": 20}
        }

        questions = self.generator.generate(config, quantity=10, question_type="FILL_BLANK")
        self.assertEqual(len(questions), 10)

        # 验证 rendering_meta 中存在
        for q in questions:
            self.assertIn("rendering_meta", q)


class TestUnitConversionIntegration(unittest.TestCase):
    """单位换算综合生成器集成测试"""

    def test_generator_registration(self):
        """测试生成器是否已注册"""
        from services.template.generators import get_generator

        gen = get_generator("unit_conversion_comprehensive")
        self.assertIsNotNone(gen)
        self.assertIsInstance(gen, UnitConversionComprehensiveGenerator)

    def test_end_to_end_currency(self):
        """测试人民币换算端到端"""
        from services.template.generators import get_generator

        generator = get_generator("unit_conversion_comprehensive")

        config = {
            "unit_category": "currency",
            "grade_level": "grade1",
            "convert_types": ["yuan_to_jiao", "jiao_to_fen", "yuan_jiao_to_jiao"],
            "value_range": {"min": 1, "max": 20}
        }

        questions = generator.generate(config, quantity=20, question_type="CALCULATION")
        self.assertEqual(len(questions), 20)

        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("[BLANK]", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_end_to_end_length(self):
        """测试长度换算端到端"""
        from services.template.generators import get_generator

        generator = get_generator("unit_conversion_comprehensive")

        config = {
            "unit_category": "length",
            "grade_level": "grade3",
            "convert_types": ["km_to_m", "m_to_km", "m_cm_to_cm"],
            "value_range": {"min": 1, "max": 50}
        }

        questions = generator.generate(config, quantity=20, question_type="CALCULATION")
        self.assertEqual(len(questions), 20)

        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("[BLANK]", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_end_to_end_volume(self):
        """测试体积换算端到端"""
        from services.template.generators import get_generator

        generator = get_generator("unit_conversion_comprehensive")

        config = {
            "unit_category": "volume",
            "grade_level": "grade5",
            "convert_types": [
                "m3_to_dm3", "dm3_to_cm3", "l_to_ml",
                "dm3_to_l", "l_to_dm3", "cm3_to_ml"
            ],
            "value_range": {"min": 1, "max": 50}
        }

        questions = generator.generate(config, quantity=30, question_type="CALCULATION")
        self.assertEqual(len(questions), 30)

        for q in questions:
            self.assertEqual(q["type"], "CALCULATION")
            self.assertIn("[BLANK]", q["stem"])
            self.assertGreater(len(q["knowledge_points"]), 0)

    def test_comprehensive_all_categories(self):
        """测试所有单位类别"""
        from services.template.generators import get_generator

        generator = get_generator("unit_conversion_comprehensive")

        # 测试所有类别
        categories = [
            ("currency", ["yuan_to_jiao", "jiao_to_fen"]),
            ("length", ["m_to_cm", "km_to_m"]),
            ("mass", ["kg_to_g", "t_to_kg"]),
            ("area", ["m2_to_dm2", "hectare_to_m2"]),
            ("volume", ["m3_to_dm3", "l_to_ml"]),
            ("time", ["hour_to_minute", "year_to_month"]),
        ]

        for category, convert_types in categories:
            config = {
                "unit_category": category,
                "convert_types": convert_types,
                "value_range": {"min": 1, "max": 20}
            }

            questions = generator.generate(config, quantity=5, question_type="CALCULATION")
            self.assertEqual(len(questions), 5, f"类别 {category} 生成失败")


if __name__ == "__main__":
    unittest.main()
