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
    """迁移知识点数据到数据库（扁平结构）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    total_points = 0

    print("开始迁移知识点数据...")

    # 遍历 KNOWLEDGE_POINTS 字典
    for subject_code, grades in KNOWLEDGE_POINTS.items():
        for grade_code, semesters in grades.items():
            for semester_code, textbook_versions in semesters.items():
                for textbook_version_code, knowledge_points in textbook_versions.items():
                    print(f"  处理：{subject_code}/{grade_code}/{semester_code}/{textbook_version_code}")

                    # 直接插入知识点（扁平结构）
                    for sort_order, kp_name in enumerate(knowledge_points, start=1):
                        cursor.execute("""
                            INSERT INTO knowledge_points
                            (name, subject_code, grade_code, semester_code, textbook_version_code, sort_order, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, 1)
                        """, (kp_name, subject_code, grade_code, semester_code, textbook_version_code, sort_order))
                        total_points += 1

    conn.commit()

    print(f"迁移完成！")
    print(f"  - 知识点明细：{total_points} 个")

    conn.close()


if __name__ == "__main__":
    migrate_knowledge_points()
