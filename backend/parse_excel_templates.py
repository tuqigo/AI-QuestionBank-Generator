#!/usr/bin/env python3
"""
解析 Excel 文件中的题目模板，并将其转换为 QuestionTemplate 对象列表
"""

import pandas as pd
import json
from typing import List, Optional
from models.question_template import QuestionTemplate

# 导入常量定义
from core.constants import (
    SUPPORTED_SUBJECTS,
    SUPPORTED_GRADES,
    SUPPORTED_SEMESTERS,
    SUPPORTED_TEXTBOOK_VERSIONS,
    SUPPORTED_QUESTION_TYPES
)


def parse_excel_to_templates(excel_file_path: str) -> List[QuestionTemplate]:
    """
    解析 Excel 文件并返回 QuestionTemplate 对象列表

    Args:
        excel_file_path: Excel 文件路径

    Returns:
        QuestionTemplate 对象列表
    """
    # 读取 Excel 文件
    df = pd.read_excel(excel_file_path, engine='openpyxl')

    print(f"Excel 文件共有 {len(df)} 行数据")
    print(f"列名: {df.columns.tolist()}")
    print("\n前几行数据:")
    print(df.head())
    # 年级	,学期	教材版本	题型	知识点	模板名称	例题
    # 验证Excel中是否包含所有必需的主要字段
    required_main_columns = ['年级','学期', '教材版本', '题型','知识点', '模板名称', '例题']
    actual_columns = list(df.columns)

    missing_columns = []
    for col in required_main_columns:
        if col not in actual_columns:
            missing_columns.append(col)

    if missing_columns:
        raise ValueError(f"Excel文件缺少必需的字段: {missing_columns}。实际字段为: {actual_columns}")

    templates = []

    for index, row in df.iterrows():
        # 实际Excel列结构是: ['年级','学期', '教材版本', '题型','知识点', '模板名称', '例题']

        grade = str(row.iloc[0]) if len(row) > 0 and pd.notna(row.iloc[0]) else ''
        semester = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[0]) else ''
        textbook_version = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else ''
        question_type = str(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else ''
        # 获取知识点字段
        knowledge_point_raw = str(row.iloc[4]) if len(row) > 4 and pd.notna(row.iloc[4]) else ''
        name = str(row.iloc[5]) if len(row) > 5 and pd.notna(row.iloc[5]) else ''
        example = str(row.iloc[6]) if len(row) > 6 and pd.notna(row.iloc[6]) else ''

        # 固定subject为数学
        subject = "math"

        # 检查是否有缺失字段（脏数据）
        if not all([grade, semester, textbook_version, question_type, name, example]):
            print(f"警告: 第 {index + 1} 行存在缺失数据，跳过此行。")
            continue

        # 验证各项数据是否合法
        # 验证grade
        grade_key = None
        for k, v in SUPPORTED_GRADES.items():
            if grade == v or k == grade:
                grade_key = k
                break

        if not grade_key:
            print(f"警告: 第 {index + 1} 行年级 '{grade}' 不合法，跳过此行。")
            continue

        # 验证semester
        semester_key = None
        for k, v in SUPPORTED_SEMESTERS.items():
            if semester == v or k == semester:
                semester_key = k
                break

        if not semester_key:
            print(f"警告: 第 {index + 1} 行学期 '{semester}' 不合法，跳过此行。")
            continue

        # 验证textbook_version
        textbook_version_key = None
        for k, v_data in SUPPORTED_TEXTBOOK_VERSIONS.items():
            if textbook_version == v_data["name"] or k == textbook_version:
                textbook_version_key = k
                break

        # 如果没找到完全匹配，尝试模糊匹配
        if not textbook_version_key:
            # 处理"沪教版（2024新版）" -> "hj"
            if "沪教版" in textbook_version and "2024" in textbook_version:
                textbook_version_key = "hj"
            elif "人教版" in textbook_version and "2024" in textbook_version:
                textbook_version_key = "rjb_2024"
            elif "人教版" in textbook_version:
                textbook_version_key = "rjb"
            elif "沪教版" in textbook_version:
                textbook_version_key = "hj"

        if not textbook_version_key:
            print(f"警告: 第 {index + 1} 行教材版本 '{textbook_version}' 不合法，跳过此行。")
            continue

        # 验证question_type
        question_type_key = None
        for k, (v, _) in SUPPORTED_QUESTION_TYPES.items():
            if question_type == v or k == question_type:
                question_type_key = k
                break

        # 如果没找到完全匹配，尝试模糊匹配
        if not question_type_key:
            # 根据关键词判断题型
            if "计算" in question_type or "口算" in question_type or "算式" in question_type:
                question_type_key = "CALCULATION"
            elif "选择" in question_type or "单选" in question_type:
                question_type_key = "SINGLE_CHOICE"
            elif "填空" in question_type:
                question_type_key = "FILL_BLANK"
            elif "应用" in question_type:
                question_type_key = "WORD_PROBLEM"
            elif "口算" in question_type:
                question_type_key = "ORAL_CALCULATION"

        if not question_type_key:
            print(f"警告: 第 {index + 1} 行题型 '{question_type}' 不合法，跳过此行。")
            continue

        # 获取知识点字段
        knowledge_point_raw = str(row.iloc[4]) if len(row) > 4 and pd.notna(row.iloc[4]) else ''
        name = str(row.iloc[5]) if len(row) > 5 and pd.notna(row.iloc[5]) else ''
        example = str(row.iloc[6]) if len(row) > 6 and pd.notna(row.iloc[6]) else ''

        # 从示例中推断模板模式和变量配置
        template_pattern = _extract_template_pattern(example, name)
        variables_config = _infer_variables_config(example, name)

        # 简单尝试从知识点原始数据中提取ID或匹配现有知识
        knowledge_point_id = _match_knowledge_point_id(knowledge_point_raw, subject, grade_key, semester_key, textbook_version_key)

        # 尝试从示例中推断模板模式
        if not example:
            print(f"警告: 第 {index + 1} 行example '{example}' 不合法，跳过此行。")
            continue

        # 构造模板对象
        template = QuestionTemplate(
            id=None,  # 新创建的对象 ID 为 None，后续可以插入数据库时分配
            name=name,
            subject=subject,  # 固定为数学
            grade=grade_key,  # 使用标准键值
            semester=semester_key,  # 使用标准键值
            textbook_version=textbook_version_key,  # 使用标准键值
            question_type=question_type_key,  # 使用标准键值
            template_pattern=template_pattern,  # 新增字段
            variables_config=variables_config,  # 新增字段
            knowledge_point_id=knowledge_point_id,  # 新增字段
            example=example,
            is_active=True
        )

        templates.append(template)

    return templates


def _extract_template_pattern(example: str, name: str) -> str:
    """
    从示例或名称中提取模板模式
    """
    if pd.isna(example) or example == '':
        # 如果没有示例，从名称中提取或创建基本模式
        if '比大小' in name or '比较' in name:
            return '{a} ○ {b}'
        elif '加减' in name or '计算' in name:
            return '{a} {op} {b} = '
        else:
            return '{question}'
    else:
        # 从示例中提取模式，替换具体的数值为变量占位符
        example_str = str(example)
        # 简单处理：保留特殊符号，但把数字替换成变量
        # 这里只是基础处理，真实场景中可能需要更复杂的逻辑
        if '\\bigcirc' in example_str:
            return example_str.replace('\\bigcirc', '○')  # 替换圈圈符号
        elif '=' in example_str:
            # 移除示例末尾的等号，替换为填空格式
            if example_str.endswith('='):
                return example_str[:-1].strip() + ' = （ ）'
            else:
                return example_str.split('=')[0].strip() + ' = （ ）'  # 添加填空标记
        else:
            return example_str


def _infer_variables_config(example: str, name: str) -> dict:
    """
    从示例或名称中推断变量配置
    """
    # 默认变量配置
    config = {
        "rules": ["ensure_positive"]
    }

    # 根据示例内容推断变量类型和范围
    if pd.isna(example) or example == '':
        # 如果没有示例，从名称中推断
        if '比大小' in name or '比较' in name:
            config.update({
                "a": {"min": 1, "max": 10},
                "b": {"min": 1, "max": 10}
            })
        elif '加减' in name or '计算' in name:
            config.update({
                "a": {"min": 1, "max": 20},
                "b": {"min": 1, "max": 20},
                "op": {"values": ["+", "-"]}
            })
        else:
            config.update({
                "num": {"min": 1, "max": 10}
            })
    else:
        example_str = str(example)
        # 如果示例中有特定字符，则设置相应的变量配置
        if '+' in example_str or '-' in example_str:
            # 加减法题目
            config.update({
                "a": {"min": 1, "max": 20},
                "b": {"min": 1, "max": 20},
                "op": {"values": ["+", "-"]}
            })
        elif '○' in example_str or '○' in example_str:
            # 比大小题目
            config.update({
                "a": {"min": 1, "max": 10},
                "b": {"min": 1, "max": 10}
            })
        elif '=' in example_str:
            # 计算题
            config.update({
                "a": {"min": 1, "max": 20},
                "b": {"min": 1, "max": 20},
                "op": {"values": ["+", "-", "*", "/"]}
            })
        else:
            # 默认配置
            config.update({
                "num": {"min": 1, "max": 10}
            })

    return config


def _match_knowledge_point_id(knowledge_point_raw: str, subject: str, grade: str, semester: str, textbook_version: str) -> Optional[int]:
    """
    尝试匹配知识点ID，这里我们简化处理，直接返回None，
    在实际应用中，这应该查询数据库以找到匹配的知识点ID
    """
    # 在当前实现中，我们暂不实现精确匹配，返回None
    # 实际应用中应该根据 subject, grade, semester, textbook_version 和 knowledge_point_raw
    # 来查找或创建知识点ID
    return None


def print_templates_summary(templates: List[QuestionTemplate]):
    """打印模板列表摘要"""
    print(f"\n======= 解析结果摘要 =======")
    print(f"共解析出 {len(templates)} 个模板")

    if templates:
        print(f"\n已成功解析前10个模板预览:")
        # 只打印前10个模板避免编码错误
        for i, template in enumerate(templates[:10], 1):
            print(f"\n--- 模板 {i} ---")
            print(f"名称: {repr(template.name)}")
            print(f"学科: {repr(template.subject)}")
            print(f"年级: {repr(template.grade)}")
            print(f"学期: {repr(template.semester)}")
            print(f"教材版本: {repr(template.textbook_version)}")
            print(f"题型: {repr(template.question_type)}")
            print(f"模板模式: {repr(template.template_pattern)}")  # 修改为 template_pattern 而不是 example
            print(f"变量配置: {template.variables_config}")
            print(f"知识点ID: {template.knowledge_point_id}")

        if len(templates) > 10:
            print(f"\n... 还有 {len(templates) - 10} 个模板未显示")

    else:
        print("未能解析出任何模板，请检查输入数据。")


if __name__ == "__main__":
    excel_file_path = "nice.xlsx"

    try:
        templates = parse_excel_to_templates(excel_file_path)
        print_templates_summary(templates)

        # 可选：将结果保存到文件
        print(f"\n======= 完成 =======")
        print(f"所有 QuestionTemplate 对象已创建并存储在 'templates' 列表中。")
        print(f"可以进一步将这些模板存入数据库或进行其他处理。")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {excel_file_path}")
        print("请确保 Excel 文件位于正确的路径下")
    except Exception as e:
        print(f"解析 Excel 文件时出错: {e}")
        import traceback
        traceback.print_exc()