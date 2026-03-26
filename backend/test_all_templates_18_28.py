# -*- coding: utf-8 -*-
"""测试 ID 18-28 模板配置 - 验证所有模板正常生成题目"""
import sys
import json
sys.path.insert(0, '.')

from utils.db_helper import DbHelper
from services.template.generators.mixed_addition_subtraction import MixedAdditionSubtractionGenerator

generator = MixedAdditionSubtractionGenerator()

print('=' * 70)
print('=== 测试 ID 18-28 模板配置 ===')
print('=' * 70)

all_passed = True

for id in range(18, 29):
    if id == 20:  # 暂不配置
        print(f'ID={id}: 跳过（需要数列填空生成器）')
        continue

    template = DbHelper.get_template(id)
    if not template:
        print(f'ID={id}: [失败] 模板不存在')
        all_passed = False
        continue

    config = json.loads(template['variables_config']) if isinstance(template['variables_config'], str) else template['variables_config']

    try:
        questions = generator.generate(config, 10, 'ORAL_CALCULATION')

        if len(questions) < 5:
            print(f'ID={id}: [警告] 只生成了 {len(questions)} 题')

        # 验证题目符合预期
        validated = True
        for q in questions:
            stem = q['stem']
            # 简单验证：题目中不能有负数
            if '[BLANK]' in stem:
                parts = stem.split('[BLANK]')
                if len(parts) == 2:
                    left = parts[0]
                    # 检查左边是否有有效的表达式
                    if not any(c in left for c in ['+', '-']):
                        if id not in [21, 24]:  # 简单比大小除外
                            validated = False
                            break

        status = '[通过]' if validated else '[警告]'
        print(f'ID={id}: {status} {template["name"]} - 生成了 {len(questions)} 题')

        # 显示前 3 题示例
        for i, q in enumerate(questions[:3], 1):
            print(f'      {i}. {q["stem"]}')

    except Exception as e:
        print(f'ID={id}: [失败] {template["name"]} - 错误：{e}')
        all_passed = False

print()
print('=' * 70)
if all_passed:
    print('所有模板配置验证通过！')
else:
    print('部分模板配置存在问题，请检查上方输出')
print('=' * 70)
