"""
学科数据访问服务
"""
import sqlite3
from typing import List, Optional
from models.config import SubjectInDB, SubjectCreate, SubjectUpdate
from config import DB_PATH


class SubjectStore:
    """学科数据访问类"""

    @staticmethod
    def get_all(active_only: bool = True) -> List[SubjectInDB]:
        """
        获取所有学科

        Args:
            active_only: 是否只获取启用的学科

        Returns:
            学科列表
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            if active_only:
                cursor = conn.execute(
                    "SELECT * FROM subjects WHERE is_active = 1 ORDER BY sort_order"
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM subjects ORDER BY sort_order"
                )
            return [SubjectInDB(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(id: int) -> Optional[SubjectInDB]:
        """
        根据 ID 获取学科

        Args:
            id: 学科 ID

        Returns:
            学科对象，不存在返回 None
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM subjects WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return SubjectInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_code(code: str) -> Optional[SubjectInDB]:
        """
        根据代码获取学科

        Args:
            code: 学科代码

        Returns:
            学科对象，不存在返回 None
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                "SELECT * FROM subjects WHERE code = ?",
                (code,)
            )
            row = cursor.fetchone()
            return SubjectInDB(**dict(row)) if row else None
        finally:
            conn.close()

    @staticmethod
    def create(input_data: SubjectCreate) -> SubjectInDB:
        """
        创建学科

        Args:
            input_data: 创建请求数据

        Returns:
            创建的学科对象
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(
                """
                INSERT INTO subjects (code, name_zh, sort_order, is_active)
                VALUES (?, ?, ?, 1)
                """,
                (input_data.code, input_data.name_zh, input_data.sort_order)
            )
            conn.commit()

            # 获取刚插入的记录
            cursor = conn.execute(
                "SELECT * FROM subjects WHERE id = ?",
                (cursor.lastrowid,)
            )
            row = cursor.fetchone()
            return SubjectInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def update(id: int, input_data: SubjectUpdate) -> Optional[SubjectInDB]:
        """
        更新学科

        Args:
            id: 学科 ID
            input_data: 更新数据

        Returns:
            更新后的学科对象，不存在返回 None
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            # 构建动态更新语句
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
                # 没有更新内容，直接返回当前数据
                cursor = conn.execute(
                    "SELECT * FROM subjects WHERE id = ?",
                    (id,)
                )
                row = cursor.fetchone()
                return SubjectInDB(**dict(row)) if row else None

            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(id)

            cursor = conn.execute(
                f"UPDATE subjects SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

            if cursor.rowcount == 0:
                return None

            cursor = conn.execute(
                "SELECT * FROM subjects WHERE id = ?",
                (id,)
            )
            row = cursor.fetchone()
            return SubjectInDB(**dict(row))
        finally:
            conn.close()

    @staticmethod
    def delete(id: int) -> bool:
        """
        删除学科（软删除，设为 is_active=0）

        Args:
            id: 学科 ID

        Returns:
            是否删除成功
        """
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(
                "UPDATE subjects SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def hard_delete(id: int) -> bool:
        """
        硬删除学科（谨慎使用）

        Args:
            id: 学科 ID

        Returns:
            是否删除成功
        """
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(
                "DELETE FROM subjects WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_as_options() -> List[dict]:
        """
        获取学科选项列表（用于下拉框）

        Returns:
            选项列表 [{"value": code, "label": name_zh}]
        """
        subjects = SubjectStore.get_all()
        return [{"value": s.code, "label": s.name_zh} for s in subjects]
