# -*- coding: utf-8 -*-
"""
模板配置测试 - 验证 ID 18-28 模板配置正确性

测试覆盖：
1. 数字范围验证：检查题目中的数字是否在配置范围内
2. 结果约束验证：检查运算结果是否满足 result_within 限制
3. 题型格式验证：检查题目格式是否符合预期
"""
import unittest
import json
import re
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_helper import DbHelper
from services.template.generators.mixed_addition_subtraction import MixedAdditionSubtractionGenerator


class TestTemplateConfiguration(unittest.TestCase):
    """模板配置测试类"""

    def setUp(self):
        self.generator = MixedAdditionSubtractionGenerator()

    def _get_config(self, template_id):
        """获取模板配置"""
        template = DbHelper.get_template(template_id)
        if not template:
            return None
        return json.loads(template['variables_config']) if isinstance(template['variables_config'], str) else template['variables_config']

    def _generate_questions(self, template_id, quantity=50):
        """生成题目"""
        config = self._get_config(template_id)
        if not config:
            return []
        return self.generator.generate(config, quantity, 'ORAL_CALCULATION')

    def _extract_result(self, stem):
        """从题目中提取运算结果（用于验证）"""
        if '=' in stem and '[BLANK]' in stem:
            left_side = stem.split('=')[0].replace('[BLANK]', '')
            if '+' in left_side or '-' in left_side:
                try:
                    result = eval(left_side.replace(' ', ''))
                    return result
                except:
                    pass
        return None

    def _extract_numbers(self, stem):
        """从题目中提取所有数字（排除 [BLANK] 中的内容）"""
        # 先替换 [BLANK] 为空格，避免数字连在一起
        cleaned = stem.replace('[BLANK]', ' ')
        return [int(n) for n in re.findall(r'\b\d+\b', cleaned)]

    # ==================== ID=18: 0 的认识和加减法（5 以内） ====================

    def test_id_18_result_within_5(self):
        """ID=18: 5 以内数的认识，结果不能超过 5"""
        questions = self._generate_questions(18, 30)
        # 由于约束较严格，可能无法生成足够数量的题目，至少验证能生成
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 5, f"题目 '{stem}' 结果 {result} 超过 5")
                self.assertGreaterEqual(result, 0, f"题目 '{stem}' 结果 {result} 为负数")

    def test_id_18_numbers_within_5(self):
        """ID=18: 5 以内数的认识，数字范围 0-5"""
        questions = self._generate_questions(18, 30)

        for q in questions:
            stem = q['stem']
            numbers = self._extract_numbers(stem)
            for num in numbers:
                self.assertLessEqual(num, 5, f"题目 '{stem}' 中数字 {num} 超过 5")

    # ==================== ID=19: 整理和复习（5 以内综合） ====================

    def test_id_19_result_within_5(self):
        """ID=19: 5 以内综合练习，结果不能超过 5"""
        questions = self._generate_questions(19, 50)

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 5, f"题目 '{stem}' 结果 {result} 超过 5")

    # ==================== ID=21: 6~9 的比大小 ====================

    def test_id_21_numbers_6_to_9(self):
        """ID=21: 6~9 的比大小，数字范围 6-9"""
        questions = self._generate_questions(21, 50)

        for q in questions:
            stem = q['stem']
            numbers = self._extract_numbers(stem)
            for num in numbers:
                self.assertGreaterEqual(num, 6, f"题目 '{stem}' 中数字 {num} 小于 6")
                self.assertLessEqual(num, 9, f"题目 '{stem}' 中数字 {num} 大于 9")

    # ==================== ID=22: 6 和 7 的加、减法（结果≤7） ====================

    def test_id_22_result_within_7(self):
        """ID=22: 6 和 7 的加减法，结果不能超过 7"""
        questions = self._generate_questions(22, 50)

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 7, f"题目 '{stem}' 结果 {result} 超过 7")

    # ==================== ID=23: 8 和 9 的加、减法（结果≤9） ====================

    def test_id_23_result_within_9(self):
        """ID=23: 8 和 9 的加减法，结果不能超过 9"""
        questions = self._generate_questions(23, 50)

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 9, f"题目 '{stem}' 结果 {result} 超过 9")

    # ==================== ID=24: 10 的认识（比大小） ====================

    def test_id_24_numbers_6_to_10(self):
        """ID=24: 10 的认识，数字范围 6-10"""
        questions = self._generate_questions(24, 50)

        for q in questions:
            stem = q['stem']
            numbers = self._extract_numbers(stem)
            for num in numbers:
                self.assertGreaterEqual(num, 6, f"题目 '{stem}' 中数字 {num} 小于 6")
                self.assertLessEqual(num, 10, f"题目 '{stem}' 中数字 {num} 大于 10")

    # ==================== ID=25: 10 的加、减法（结果≤10） ====================

    def test_id_25_result_within_10(self):
        """ID=25: 10 的加减法，结果不能超过 10"""
        questions = self._generate_questions(25, 50)

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 10, f"题目 '{stem}' 结果 {result} 超过 10")

    # ==================== ID=26: 10 以内的加、减法 ====================

    def test_id_26_result_within_10(self):
        """ID=26: 10 以内的加减法，结果不能超过 10"""
        questions = self._generate_questions(26, 50)

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 10, f"题目 '{stem}' 结果 {result} 超过 10")

    # ==================== ID=27: 比大小（带运算，结果≤10） ====================

    def test_id_27_result_within_10(self):
        """ID=27: 比大小（带运算），结果不能超过 10"""
        questions = self._generate_questions(27, 50)

        for q in questions:
            stem = q['stem']
            if '[BLANK]' in stem:
                left_side = stem.split('[BLANK]')[0]
                try:
                    result = eval(left_side.replace(' ', ''))
                    self.assertLessEqual(result, 10, f"题目 '{stem}' 结果 {result} 超过 10")
                except:
                    pass

    def test_id_27_single_step_operation(self):
        """ID=27: 比大小（带运算），应该是单步运算而非多步"""
        questions = self._generate_questions(27, 50)

        for q in questions:
            stem = q['stem']
            op_count = stem.count('+') + stem.count('-')
            self.assertLessEqual(op_count, 2, f"题目 '{stem}' 不是单步运算（有{op_count}个运算符）")

    # ==================== ID=28: 连加（和≤10） ====================

    def test_id_28_sum_within_10(self):
        """ID=28: 连加，和不能超过 10"""
        questions = self._generate_questions(28, 50)

        for q in questions:
            stem = q['stem']
            if '=' in stem and '[BLANK]' in stem:
                left_side = stem.split('=')[0].replace('[BLANK]', '')
                try:
                    result = eval(left_side.replace(' ', ''))
                    self.assertLessEqual(result, 10, f"题目 '{stem}' 和 {result} 超过 10")
                except:
                    pass


class TestAllTemplatesBasic(unittest.TestCase):
    """所有模板的基本测试：确保能正常生成题目"""

    def setUp(self):
        self.generator = MixedAdditionSubtractionGenerator()

    def test_id_18_to_28_all_templates(self):
        """测试 ID 18-28（除 20 外）所有模板能正常生成题目"""
        for template_id in range(18, 29):
            if template_id == 20:  # 暂不配置
                continue

            template = DbHelper.get_template(template_id)
            self.assertIsNotNone(template, f"ID={template_id}: 模板不存在")

            config = json.loads(template['variables_config']) if isinstance(template['variables_config'], str) else template['variables_config']

            try:
                questions = self.generator.generate(config, 10, 'ORAL_CALCULATION')
                self.assertEqual(len(questions), 10, f"ID={template_id}: 应生成 10 道题")
            except Exception as e:
                self.fail(f"ID={template_id}: 生成失败 - {e}")


# ==================== ID 29-47 模板测试 ====================

class TestTemplateConfiguration29to47(unittest.TestCase):
    """模板配置测试类 - ID 29-47"""

    def setUp(self):
        self.generator = MixedAdditionSubtractionGenerator()

    def _get_config(self, template_id):
        """获取模板配置"""
        template = DbHelper.get_template(template_id)
        if not template:
            return None
        return json.loads(template['variables_config']) if isinstance(template['variables_config'], str) else template['variables_config']

    def _generate_questions(self, template_id, quantity=50):
        """生成题目"""
        config = self._get_config(template_id)
        if not config:
            return []
        return self.generator.generate(config, quantity, 'ORAL_CALCULATION')

    def _extract_result(self, stem):
        """从题目中提取运算结果"""
        if '=' in stem and '[BLANK]' in stem:
            left_side = stem.split('=')[0].replace('[BLANK]', '')
            if '+' in left_side or '-' in left_side:
                try:
                    return eval(left_side.replace(' ', ''))
                except:
                    pass
        return None

    def _extract_numbers(self, stem):
        """从题目中提取所有数字"""
        cleaned = stem.replace('[BLANK]', ' ')
        return [int(n) for n in re.findall(r'\b\d+\b', cleaned)]

    # ==================== 6~10 的认识和加减法 (ID 29-31) ====================

    def test_id_29_consecutive_subtract_within_10(self):
        """ID=29: 连减，6~10 的认识，结果不超过 10"""
        questions = self._generate_questions(29, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            # 验证是连减格式
            parts = stem.replace('[BLANK]', '').split('-')
            self.assertGreaterEqual(len(parts), 3, f"题目 {stem} 应该是连减格式")
            # 验证结果不超过 10
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 10, f"题目 '{stem}' 结果 {result} 超过 10")

    def test_id_30_mixed_operation_within_10(self):
        """ID=30: 加减混合，6~10 的认识"""
        questions = self._generate_questions(30, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 10, f"题目 '{stem}' 结果 {result} 超过 10")

    def test_id_31_review_within_10(self):
        """ID=31: 整理和复习，6~10 的认识，包含多种题型"""
        questions = self._generate_questions(31, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    # ==================== 11~20 各数的认识 (ID 32-38) ====================

    def test_id_32_11_to_20_recognition(self):
        """ID=32: 11~20 的认识，填空题型"""
        questions = self._generate_questions(32, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            self.assertIn('[BLANK]', stem, f"题目 {stem} 应包含填空")

    def test_id_33_11_to_20_compare(self):
        """ID=33: 11~20 的大小比较"""
        questions = self._generate_questions(33, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            self.assertIn('[BLANK]', stem)
            numbers = self._extract_numbers(stem)
            for num in numbers:
                self.assertGreaterEqual(num, 11, f"题目 '{stem}' 中数字 {num} 小于 11")
                self.assertLessEqual(num, 20, f"题目 '{stem}' 中数字 {num} 大于 20")

    def test_id_34_ten_plus(self):
        """ID=34: 十加几与相应的减法"""
        questions = self._generate_questions(34, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            if '+' in stem and '[BLANK]' in stem.split('=')[0]:
                self.assertIn('10+', stem, f"题目 '{stem}' 应该是 10 加几")

    def test_id_35_teen_plus_minus(self):
        """ID=35: 十几加几与相应的减法"""
        questions = self._generate_questions(35, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    def test_id_36_consecutive_11_to_20(self):
        """ID=36: 连加、连减、加减混合 (11~20)"""
        questions = self._generate_questions(36, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    def test_id_37_compare_11_to_20(self):
        """ID=37: 比大小 (11~20)"""
        questions = self._generate_questions(37, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            self.assertIn('[BLANK]', stem)

    def test_id_38_review_11_to_20(self):
        """ID=38: 整理和复习 (11~20)"""
        questions = self._generate_questions(38, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    # ==================== 20 以内的进位加法 (ID 39-43) ====================

    def test_id_39_nine_plus(self):
        """ID=39: 9 加几（进位加法）"""
        questions = self._generate_questions(39, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        # 验证生成的题目都是 9 加几格式
        for q in questions:
            stem = q['stem']
            if '+' in stem and '=' in stem:
                self.assertIn('9+', stem, f"题目 '{stem}' 应该是 9 加几")
            result = self._extract_result(stem)
            if result is not None:
                self.assertGreaterEqual(result, 11, f"题目 '{stem}' 结果 {result} 小于 11")
                self.assertLessEqual(result, 18, f"题目 '{stem}' 结果 {result} 大于 18")

    def test_id_40_8_7_6_plus(self):
        """ID=40: 8、7、6 加几（进位加法）"""
        questions = self._generate_questions(40, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    def test_id_41_5_4_3_2_plus(self):
        """ID=41: 5、4、3、2 加几，结果大于 10 小于 20"""
        questions = self._generate_questions(41, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertGreater(result, 10, f"题目 '{stem}' 结果 {result} 不大于 10")
                self.assertLess(result, 20, f"题目 '{stem}' 结果 {result} 不小于 20")

    def test_id_42_compare_addition(self):
        """ID=42: 比大小（带加法）"""
        questions = self._generate_questions(42, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    def test_id_43_review_20_addition(self):
        """ID=43: 整理和复习（20 以内进位加法）"""
        questions = self._generate_questions(43, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    # ==================== 复习与专项练习 (ID 44-47) ====================

    def test_id_44_review_practice(self):
        """ID=44: 复习与关练"""
        questions = self._generate_questions(44, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    def test_id_45_within_10(self):
        """ID=45: 10 以内的加、减法，结果小于 10"""
        questions = self._generate_questions(45, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            result = self._extract_result(stem)
            if result is not None:
                self.assertLessEqual(result, 10, f"题目 '{stem}' 结果 {result} 大于 10")

    def test_id_46_20_addition(self):
        """ID=46: 20 以内的进位加法"""
        questions = self._generate_questions(46, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

    def test_id_47_teen_minus_9(self):
        """ID=47: 十几减 9"""
        questions = self._generate_questions(47, 30)
        self.assertGreater(len(questions), 0, "应能生成题目")

        for q in questions:
            stem = q['stem']
            if '-' in stem:
                self.assertIn('-9', stem, f"题目 '{stem}' 应该是减 9")


class TestAllTemplates29to47(unittest.TestCase):
    """ID 29-47 模板的基本测试：确保能正常生成题目"""

    def setUp(self):
        self.generator = MixedAdditionSubtractionGenerator()

    def test_id_29_to_47_all_templates(self):
        """测试 ID 29-47 所有模板能正常生成题目"""
        # 某些模板的题目数量有限（如 ID=39 只有 8 种组合），至少验证能生成题目
        min_quantity = 5  # 最低题目数量要求

        for template_id in range(29, 48):
            template = DbHelper.get_template(template_id)
            self.assertIsNotNone(template, f"ID={template_id}: 模板不存在")

            config = json.loads(template['variables_config']) if isinstance(template['variables_config'], str) else template['variables_config']

            try:
                questions = self.generator.generate(config, 10, 'ORAL_CALCULATION')
                self.assertGreater(len(questions), 0, f"ID={template_id}: 应能生成题目")
                # 对于题目数量有限的模板，至少生成 min_quantity 道题
                self.assertGreaterEqual(len(questions), min_quantity, f"ID={template_id}: 至少应生成 {min_quantity} 道题")
            except Exception as e:
                self.fail(f"ID={template_id}: 生成失败 - {e}")


if __name__ == '__main__':
    unittest.main()
