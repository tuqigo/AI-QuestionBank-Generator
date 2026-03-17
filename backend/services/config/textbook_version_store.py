"""
教材版本数据访问服务
"""
import sqlite3
from typing import List, Optional
from models.config import TextbookVersionInDB, TextbookVersionCreate, TextbookVersionUpdate
from config import DB_PATH


class TextbookVersionStore:
    """教材版本数据访问类"""

    @staticmethod
    def get_all(active_only: bool = True) -> List[TextbookVersionInDB]:
        """获取所有教材版本"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            if active_only:
                cursor = conn.execute(
                    "SELECT * FROM textbook_versions WHERE is_active = 1 ORDER BY sort_order"
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM textbook_versions ORDER BY sort_order"
                )
            return [TextbookVersionInDB(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(id: int) -> Optional[TextbookVersionInDB]:
        """根据 ID 获取教材版本"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM textbook_versions WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return TextbookVersionInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_code(code: str) -> Optional[TextbookVersionInDB]:
        """根据代码获取教材版本"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM textbook_versions WHERE version_code = ?",
                (code,)
            )
            row = cursor.fetchone()
            return TextbookVersionInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def create(input_data: TextbookVersionCreate) -> TextbookVersionInDB:
        """创建教材版本"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                """
                INSERT INTO textbook_versions (version_code, name_zh, sort_order, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (input_data.version_code, input_data.name_zh, input_data.sort_order)
            )
            conn.commit()

            cursor = conn.execute(
                "SELECT * FROM textbook_versions WHERE id = ?",
                (cursor.lastrowid,)
            )
            row = cursor.fetchone()
            return TextbookVersionInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def update(id: int, input_data: TextbookVersionUpdate) -> Optional[TextbookVersionInDB]:
        """更新教材版本"""
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
                    "SELECT * FROM textbook_versions WHERE id = ?",
                    (id,)
                )
                row = cursor.fetchone()
                return TextbookVersionInDB(**dict(row)) if row else None

            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(id)

            cursor = conn.execute(
                f"UPDATE textbook_versions SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

            if cursor.rowcount == 0:
                return None

            cursor = conn.execute(
                "SELECT * FROM textbook_versions WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return TextbookVersionInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def delete(id: int) -> bool:
        """删除教材版本（软删除）"""
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(
                "UPDATE textbook_versions SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_as_options() -> List[dict]:
        """获取教材版本选项列表"""
        versions = TextbookVersionStore.get_all()
        return [{"id": v.version_code, "name": v.name_zh, "sort": v.sort_order} for v in versions]
