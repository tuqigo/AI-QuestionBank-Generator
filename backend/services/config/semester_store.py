"""
学期数据访问服务
"""
import sqlite3
from typing import List, Optional
from models.config import SemesterInDB, SemesterCreate, SemesterUpdate
from config import DB_PATH


class SemesterStore:
    """学期数据访问类"""

    @staticmethod
    def get_all(active_only: bool = True) -> List[SemesterInDB]:
        """获取所有学期"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            if active_only:
                cursor = conn.execute(
                    "SELECT * FROM semesters WHERE is_active = 1 ORDER BY sort_order"
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM semesters ORDER BY sort_order"
                )
            return [SemesterInDB(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(id: int) -> Optional[SemesterInDB]:
        """根据 ID 获取学期"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM semesters WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return SemesterInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_code(code: str) -> Optional[SemesterInDB]:
        """根据代码获取学期"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM semesters WHERE code = ?",
                (code,)
            )
            row = cursor.fetchone()
            return SemesterInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def create(input_data: SemesterCreate) -> SemesterInDB:
        """创建学期"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                """
                INSERT INTO semesters (code, name_zh, sort_order, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (input_data.code, input_data.name_zh, input_data.sort_order)
            )
            conn.commit()

            cursor = conn.execute(
                "SELECT * FROM semesters WHERE id = ?",
                (cursor.lastrowid,)
            )
            row = cursor.fetchone()
            return SemesterInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def update(id: int, input_data: SemesterUpdate) -> Optional[SemesterInDB]:
        """更新学期"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            updates = []
            values = []

            if input_data.name_zh is not None:
                updates.append("name_zh = ?")
                values.append(input_data.name_zh)
            if input_data.sort_order is not None:
                updates.append("sort_order = ?")
                values.append(input_data.sort_order)
            if input_data.is_active is not None:
                updates.append("is_active = ?")
                values.append(input_data.is_active)

            if not updates:
                cursor = conn.execute(
                    "SELECT * FROM semesters WHERE id = ?",
                    (id,)
                )
                row = cursor.fetchone()
                return SemesterInDB(**dict(row)) if row else None

            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(id)

            cursor = conn.execute(
                f"UPDATE semesters SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

            if cursor.rowcount == 0:
                return None

            cursor = conn.execute(
                "SELECT * FROM semesters WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return SemesterInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def delete(id: int) -> bool:
        """删除学期（软删除）"""
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(
                "UPDATE semesters SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_as_options() -> List[dict]:
        """获取学期选项列表"""
        semesters = SemesterStore.get_all()
        return [{"value": s.code, "label": s.name_zh} for s in semesters]
