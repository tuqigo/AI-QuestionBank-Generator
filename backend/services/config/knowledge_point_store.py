"""
知识点数据访问服务 - 扁平结构
"""
import sqlite3
from typing import List, Optional
from models.config import (
    KnowledgePointInDB,
    KnowledgePointCreate,
    KnowledgePointUpdate,
)
from config import DB_PATH


class KnowledgePointStore:
    """知识点数据访问类"""

    @staticmethod
    def get_all(active_only: bool = True) -> List[KnowledgePointInDB]:
        """获取所有知识点"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            if active_only:
                cursor = conn.execute(
                    "SELECT * FROM knowledge_points WHERE is_active = 1 ORDER BY sort_order"
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM knowledge_points ORDER BY sort_order"
                )
            return [KnowledgePointInDB(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(id: int) -> Optional[KnowledgePointInDB]:
        """根据 ID 获取知识点"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM knowledge_points WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return KnowledgePointInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_filters(
        subject_code: Optional[str] = None,
        grade_code: Optional[str] = None,
        semester_code: Optional[str] = None,
        textbook_version_code: Optional[str] = None,
        active_only: bool = True,
    ) -> List[KnowledgePointInDB]:
        """
        根据筛选条件获取知识点列表

        Args:
            subject_code: 学科代码筛选
            grade_code: 年级代码筛选
            semester_code: 学期代码筛选
            textbook_version_code: 教材版本代码筛选
            active_only: 是否只获取启用的知识点

        Returns:
            知识点列表
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            conditions = []
            values = []

            if active_only:
                conditions.append("is_active = 1")

            if subject_code:
                conditions.append("subject_code = ?")
                values.append(subject_code)
            if grade_code:
                conditions.append("grade_code = ?")
                values.append(grade_code)
            if semester_code:
                conditions.append("semester_code = ?")
                values.append(semester_code)
            if textbook_version_code:
                conditions.append("textbook_version_code = ?")
                values.append(textbook_version_code)

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            cursor = conn.execute(
                f"SELECT * FROM knowledge_points{where_clause} ORDER BY sort_order",
                values
            )
            return [KnowledgePointInDB(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def create(input_data: KnowledgePointCreate) -> KnowledgePointInDB:
        """创建知识点"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                """
                INSERT INTO knowledge_points
                (name, subject_code, grade_code, semester_code, textbook_version_code, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    input_data.name,
                    input_data.subject_code,
                    input_data.grade_code,
                    input_data.semester_code,
                    input_data.textbook_version_code,
                    input_data.sort_order,
                )
            )
            conn.commit()

            cursor = conn.execute(
                "SELECT * FROM knowledge_points WHERE id = ?",
                (cursor.lastrowid,)
            )
            row = cursor.fetchone()
            return KnowledgePointInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def update(id: int, input_data: KnowledgePointUpdate) -> Optional[KnowledgePointInDB]:
        """更新知识点"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            updates = []
            values = []

            if input_data.name is not None:
                updates.append("name = ?")
                values.append(input_data.name)
            if input_data.subject_code is not None:
                updates.append("subject_code = ?")
                values.append(input_data.subject_code)
            if input_data.grade_code is not None:
                updates.append("grade_code = ?")
                values.append(input_data.grade_code)
            if input_data.semester_code is not None:
                updates.append("semester_code = ?")
                values.append(input_data.semester_code)
            if input_data.textbook_version_code is not None:
                updates.append("textbook_version_code = ?")
                values.append(input_data.textbook_version_code)
            if input_data.sort_order is not None:
                updates.append("sort_order = ?")
                values.append(input_data.sort_order)
            if input_data.is_active is not None:
                updates.append("is_active = ?")
                values.append(input_data.is_active)

            if not updates:
                cursor = conn.execute(
                    "SELECT * FROM knowledge_points WHERE id = ?",
                    (id,)
                )
                row = cursor.fetchone()
                return KnowledgePointInDB(**dict(row)) if row else None

            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(id)

            cursor = conn.execute(
                f"UPDATE knowledge_points SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

            if cursor.rowcount == 0:
                return None

            cursor = conn.execute(
                "SELECT * FROM knowledge_points WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return KnowledgePointInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def delete(id: int) -> bool:
        """删除知识点（软删除）"""
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(
                "UPDATE knowledge_points SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_as_options(
        subject_code: Optional[str] = None,
        grade_code: Optional[str] = None,
        semester_code: Optional[str] = None,
        textbook_version_code: Optional[str] = None,
    ) -> List[dict]:
        """
        获取知识点选项列表（用于下拉框）

        Returns:
            选项列表 [{"id": id, "name": name}]
        """
        points = KnowledgePointStore.get_by_filters(
            subject_code=subject_code,
            grade_code=grade_code,
            semester_code=semester_code,
            textbook_version_code=textbook_version_code,
        )
        return [{"id": p.id, "name": p.name} for p in points]
