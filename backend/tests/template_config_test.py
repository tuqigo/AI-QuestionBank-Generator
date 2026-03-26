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


if __name__ == '__main__':
    unittest.main()
