"""题型数据存储库"""

import sqlite3
from typing import Optional

from models.question_type import (
    QuestionTypeCreate,
    QuestionTypeUpdate,
    QuestionTypeInDB,
)

from db import DB_PATH


class QuestionTypeStore:
    """题型数据存储库"""

    @staticmethod
    def get_connection() -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def create_table():
        """创建题型表（用于测试或手动迁移）"""
        conn = QuestionTypeStore.get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS question_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    en_name TEXT UNIQUE NOT NULL,
                    zh_name TEXT NOT NULL,
                    subject TEXT NOT NULL DEFAULT 'all',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(question_type_id: int) -> Optional[QuestionTypeInDB]:
        """根据 ID 获取题型"""
        conn = QuestionTypeStore.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM question_types WHERE id = ?",
                (question_type_id,)
            )
            row = cursor.fetchone()
            if row:
                return QuestionTypeInDB(**dict(row))
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_en_name(en_name: str) -> Optional[QuestionTypeInDB]:
        """根据英文名称获取题型"""
        conn = QuestionTypeStore.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM question_types WHERE en_name = ?",
                (en_name,)
            )
            row = cursor.fetchone()
            if row:
                return QuestionTypeInDB(**dict(row))
            return None
        finally:
            conn.close()

    @staticmethod
    def list_all(subject: Optional[str] = None, include_inactive: bool = False) -> list[QuestionTypeInDB]:
        """获取题型列表"""
        conn = QuestionTypeStore.get_connection()
        try:
            query = "SELECT * FROM question_types WHERE 1=1"
            params = []

            if not include_inactive:
                query += " AND is_active = 1"

            if subject:
                query += " AND (subject = ? OR subject = 'all')"
                params.append(subject)

            query += " ORDER BY id"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [QuestionTypeInDB(**dict(row)) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def create(question_type: QuestionTypeCreate) -> QuestionTypeInDB:
        """创建新题型"""
        conn = QuestionTypeStore.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO question_types (en_name, zh_name, subject)
                VALUES (?, ?, ?)
                """,
                (question_type.en_name, question_type.zh_name, question_type.subject)
            )
            conn.commit()

            # 获取刚插入的记录
            return QuestionTypeStore.get_by_id(cursor.lastrowid)
        finally:
            conn.close()

    @staticmethod
    def update(
        question_type_id: int,
        update_data: QuestionTypeUpdate
    ) -> Optional[QuestionTypeInDB]:
        """更新题型"""
        conn = QuestionTypeStore.get_connection()
        try:
            update_fields = []
            params = []

            if update_data.zh_name is not None:
                update_fields.append("zh_name = ?")
                params.append(update_data.zh_name)

            if update_data.subject is not None:
                update_fields.append("subject = ?")
                params.append(update_data.subject)

            if update_data.is_active is not None:
                update_fields.append("is_active = ?")
                params.append(update_data.is_active)

            if not update_fields:
                return QuestionTypeStore.get_by_id(question_type_id)

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(question_type_id)

            conn.execute(
                f"UPDATE question_types SET {', '.join(update_fields)} WHERE id = ?",
                params
            )
            conn.commit()

            return QuestionTypeStore.get_by_id(question_type_id)
        finally:
            conn.close()

    @staticmethod
    def delete(question_type_id: int) -> bool:
        """删除题型（软删除，设置为 is_active = 0）"""
        conn = QuestionTypeStore.get_connection()
        try:
            conn.execute(
                "UPDATE question_types SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (question_type_id,)
            )
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
