# -*- coding: utf-8 -*-
"""重新配置 ID 18-28 模板 - 严格控制数字范围"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, 'utf-8')

from utils.db_helper import DbHelper

print("=== 开始重新配置 ID 18-28 ===\n")

# ==================== ID=18: 0 的认识和加减法 ====================
# 知识点：5 以内数的认识 (ID=2)
# example: 3-3, 4+0 → 涉及 0 的加减法
DbHelper.update_template(18, template_pattern="{a} {op} {b}", is_active=1)
DbHelper.update_template_variables(18, {
    "num": {"min": 0, "max": 5},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["simple"],
    "rules": ["ensure_positive"],
    "result_within": 5,  # 结果不超过 5
    "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=18: 0 的认识和加减法 (5 以内，涉及 0)")

# ==================== ID=19: 整理和复习 ====================
# 知识点：5 以内数的认识 (ID=2)
# example: 2○5, 3+1, 4-1, 0+4, 3-0 → 综合练习
DbHelper.update_template(19, template_pattern="综合练习", is_active=1)
DbHelper.update_template_variables(19, {
    "num": {"min": 0, "max": 5},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["compare_simple", "simple"],
    "rules": ["ensure_different", "ensure_positive"],
    "result_within": 5,  # 结果不超过 5
    "q_type": {"compare_simple": "circle"},
    "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=19: 整理和复习 (5 以内综合)")

# ==================== ID=20: 6~9 的认识 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 2,3,(),5,6 → 数列填空，需要特殊生成器
# 暂不配置，保持原样
print("ID=20: 6~9 的认识 (数列填空，暂不配置)")

# ==================== ID=21: 6~9 的比大小 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 8○7 → 6-9 范围比大小
DbHelper.update_template(21, template_pattern="{a} \\bigcirc {b}", is_active=1)
DbHelper.update_template_variables(21, {
    "num": {"min": 6, "max": 9},
    "question_complexity": ["compare_simple"],
    "rules": ["ensure_different"],
    "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "circle", "show_question_number": True}
})
print("ID=21: 6~9 的比大小 (6-9 范围)")

# ==================== ID=22: 6 和 7 的加、减法 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 1+5, 7-4 → 结果是 6 或 7 的加减法
DbHelper.update_template(22, template_pattern="{a} {op} {b}", is_active=1)
DbHelper.update_template_variables(22, {
    "num": {"min": 1, "max": 7},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["simple"],
    "rules": ["ensure_positive"],
    "result_within": 7,  # 结果不超过 7
    "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=22: 6 和 7 的加、减法 (结果≤7)")

# ==================== ID=23: 8 和 9 的加、减法 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 3+6, 8-5 → 结果是 8 或 9 的加减法
DbHelper.update_template(23, template_pattern="{a} {op} {b}", is_active=1)
DbHelper.update_template_variables(23, {
    "num": {"min": 1, "max": 9},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["simple"],
    "rules": ["ensure_positive"],
    "result_within": 9,  # 结果不超过 9
    "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=23: 8 和 9 的加、减法 (结果≤9)")

# ==================== ID=24: 10 的认识 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 10○9 → 涉及 10 的比大小
DbHelper.update_template(24, template_pattern="{a} \\bigcirc {b}", is_active=1)
DbHelper.update_template_variables(24, {
    "num": {"min": 6, "max": 10},
    "question_complexity": ["compare_simple"],
    "rules": ["ensure_different"],
    "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "circle", "show_question_number": True}
})
print("ID=24: 10 的认识 (6-10 范围比大小)")

# ==================== ID=25: 10 的加、减法 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 3+7, 10-4 → 涉及 10 的加减法
DbHelper.update_template(25, template_pattern="{a} {op} {b}", is_active=1)
DbHelper.update_template_variables(25, {
    "num": {"min": 1, "max": 10},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["simple"],
    "rules": ["ensure_positive"],
    "result_within": 10,  # 结果不超过 10
    "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=25: 10 的加、减法 (结果≤10)")

# ==================== ID=26: 10 以内的加、减法 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 4+3, 7-5 → 10 以内的加减法
DbHelper.update_template(26, template_pattern="{a} {op} {b}", is_active=1)
DbHelper.update_template_variables(26, {
    "num": {"min": 1, "max": 10},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["simple"],
    "rules": ["ensure_positive", "result_within_10"],
    "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=26: 10 以内的加、减法 (结果≤10)")

# ==================== ID=27: 比大小（带运算） ====================
# 知识点：6~10 的认识 (ID=3)
# example: 2+4○7, 10-4○8 → 先计算再比较，数字在 6-10 范围
DbHelper.update_template(27, template_pattern="{a} {op} {b} （） {c}", is_active=1)
DbHelper.update_template_variables(27, {
    "num": {"min": 1, "max": 10},
    "op": {"values": ["+", "-"]},
    "question_complexity": ["compare_with_result"],
    "rules": ["ensure_positive", "result_within_10"],
    "q_type": {"compare_with_result": "circle"},
    "rendering_config": {"layout": "multi", "columns": 4, "font_size": 18, "answer_width": 32, "answer_style": "circle", "show_question_number": True}
})
print("ID=27: 比大小（带运算，结果≤10）")

# ==================== ID=28: 连加 ====================
# 知识点：6~10 的认识 (ID=3)
# example: 3+2+4 → 连加，和≤10
DbHelper.update_template(28, template_pattern="{a} + {b} + {c}", is_active=1)
DbHelper.update_template_variables(28, {
    "num": {"min": 1, "max": 5},
    "question_complexity": ["consecutive_add"],
    "rules": ["ensure_positive", "result_within_10"],
    "rendering_config": {"layout": "multi", "columns": 5, "font_size": 18, "answer_width": 32, "answer_style": "blank", "show_question_number": True}
})
print("ID=28: 连加 (和≤10)")

print("\n=== 配置完成 ===\n")

# 验证配置
print("=== 验证配置 ===")
for id in [18, 19, 21, 22, 23, 24, 25, 26, 27, 28]:
    template = DbHelper.get_template(id)
    if template:
        kp = DbHelper.get_knowledge_point(template['knowledge_point_id'])
        kp_name = kp['name'] if kp else 'N/A'
        print(f"ID={id}: {template['name']} | 知识点：{kp_name} | is_active={template['is_active']}")

print("\n注意：ID=20 需要数列填空生成器，暂未配置")
