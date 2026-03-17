"""
知识点数据迁移脚本
将 constants.py 中的 KNOWLEDGE_POINTS 数据迁移到数据库
"""
import sqlite3
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.constants import KNOWLEDGE_POINTS
from config import DB_PATH


def migrate_knowledge_points():
    """迁移知识点数据到数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    total_groups = 0
    total_points = 0

    print("开始迁移知识点数据...")

    # 遍历 KNOWLEDGE_POINTS 字典
    for subject_code, grades in KNOWLEDGE_POINTS.items():
        for grade_code, semesters in grades.items():
            for semester_code, textbook_versions in semesters.items():
                for textbook_version_code, knowledge_points in textbook_versions.items():
                    # 1. 插入或获取 knowledge_point_group
                    cursor.execute("""
                        INSERT OR IGNORE INTO knowledge_point_groups
                        (subject_code, grade_code, semester_code, textbook_version_code)
                        VALUES (?, ?, ?, ?)
                    """, (subject_code, grade_code, semester_code, textbook_version_code))

                    cursor.execute("""
                        SELECT id FROM knowledge_point_groups
                        WHERE subject_code = ? AND grade_code = ? AND semester_code = ? AND textbook_version_code = ?
                    """, (subject_code, grade_code, semester_code, textbook_version_code))

                    group_row = cursor.fetchone()
                    if not group_row:
                        print(f"  警告：未找到知识分组 {subject_code}/{grade_code}/{semester_code}/{textbook_version_code}")
                        continue

                    group_id = group_row['id']
                    total_groups += 1

                    # 2. 插入知识点明细
                    for sort_order, kp_name in enumerate(knowledge_points, start=1):
                        cursor.execute("""
                            INSERT OR IGNORE INTO knowledge_points
                            (group_id, name, sort_order, is_active)
                            VALUES (?, ?, ?, 1)
                        """, (group_id, kp_name, sort_order))
                        total_points += 1

    conn.commit()

    print(f"迁移完成！")
    print(f"  - 知识点分组：{total_groups} 个")
    print(f"  - 知识点明细：{total_points} 个")

    conn.close()


if __name__ == "__main__":
    migrate_knowledge_points()
