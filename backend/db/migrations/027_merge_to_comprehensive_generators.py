"""
Migration: Merge deprecated generators into comprehensive generators
Date: 2026-03-21
Description: Update question_templates to use comprehensive generators instead of deprecated ones

Changes:
  1. currency_conversion → unit_conversion_comprehensive (unit_category: currency)
  2. length_comparison → unit_conversion_comprehensive (unit_category: length)
  3. volume_conversion → unit_conversion_comprehensive (unit_category: volume)
  4. fraction_comparison → fraction_arithmetic_comparison
"""
import json
import sqlite3
from typing import Any

MIGRATION_VERSION = "027"
MIGRATION_FILENAME = "027_merge_to_comprehensive_generators.py"


def migrate(db_path: str) -> bool:
    """
    执行迁移

    Args:
        db_path: 数据库文件路径

    Returns:
        迁移是否成功
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 查找所有使用已废弃生成器的模板
        deprecated_generators = [
            'currency_conversion',
            'length_comparison',
            'volume_conversion',
            'fraction_comparison'
        ]

        placeholders = ','.join('?' * len(deprecated_generators))
        cursor.execute(f"""
            SELECT id, name, generator_module, variables_config
            FROM question_templates
            WHERE generator_module IN ({placeholders})
        """, deprecated_generators)

        templates = cursor.fetchall()
        updated_count = 0

        for template in templates:
            template_id = template['id']
            old_generator = template['generator_module']
            variables_config = template['variables_config']

            # 解析 variables_config JSON
            try:
                config = json.loads(variables_config) if variables_config else {}
            except json.JSONDecodeError:
                config = {}

            new_generator = None
            new_template_pattern = None
            new_config = config.copy()

            # 1. currency_conversion → unit_conversion_comprehensive
            if old_generator == 'currency_conversion':
                new_generator = 'unit_conversion_comprehensive'
                new_template_pattern = '单位换算：元角分之间的换算题目'
                new_config['unit_category'] = 'currency'
                # 根据模板所在的年级设置 grade_level
                # 这里不设置，让生成器使用默认值

            # 2. length_comparison → unit_conversion_comprehensive
            elif old_generator == 'length_comparison':
                new_generator = 'unit_conversion_comprehensive'
                new_template_pattern = '单位换算：长度单位之间的换算题目'
                new_config['unit_category'] = 'length'

            # 3. volume_conversion → unit_conversion_comprehensive
            elif old_generator == 'volume_conversion':
                new_generator = 'unit_conversion_comprehensive'
                new_template_pattern = '单位换算：体积/容积单位之间的换算题目'
                new_config['unit_category'] = 'volume'

            # 4. fraction_comparison → fraction_arithmetic_comparison
            elif old_generator == 'fraction_comparison':
                new_generator = 'fraction_arithmetic_comparison'
                new_template_pattern = '分数比大小：使用 LaTeX 分数格式生成两个分数进行比较'
                # 将 compare_types 转换为 operation_types（如果需要）
                if 'compare_types' in config:
                    new_config['operation_types'] = config['compare_types']

            if new_generator:
                # 更新模板记录
                cursor.execute("""
                    UPDATE question_templates
                    SET generator_module = ?,
                        template_pattern = ?,
                        variables_config = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    new_generator,
                    new_template_pattern,
                    json.dumps(new_config, ensure_ascii=False),
                    template_id
                ))
                updated_count += 1
                print(f"  更新模板 [{template_id}]: {template['name']} - {old_generator} → {new_generator}")

        conn.commit()
        print(f"迁移完成：更新了 {updated_count} 个模板")
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    from config import DB_PATH
    success = migrate(str(DB_PATH))
    if success:
        print("✅ 迁移执行成功")
    else:
        print("❌ 迁移执行失败")
