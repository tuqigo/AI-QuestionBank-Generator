"""题型数据存储库"""

from __future__ import annotations

import sqlite3
from typing import Optional, List, Dict, Any

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
                    subjects TEXT NOT NULL DEFAULT 'math,chinese,english',
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
                query += " AND (subjects LIKE ? OR subjects LIKE ?)"
                params.append(f'%{subject}%')
                params.append('%all%')

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
            # 将 subjects 列表转换为逗号分隔的字符串
            subjects_str = ','.join(question_type.subjects) if hasattr(question_type, 'subjects') and question_type.subjects else 'math,chinese,english'

            cursor = conn.execute(
                """
                INSERT INTO question_types (en_name, zh_name, subjects)
                VALUES (?, ?, ?)
                """,
                (question_type.en_name, question_type.zh_name, subjects_str)
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

            # 将 subjects 列表转换为逗号分隔的字符串
            if hasattr(update_data, 'subjects') and update_data.subjects is not None:
                update_fields.append("subjects = ?")
                params.append(','.join(update_data.subjects))

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

    @staticmethod
    def get_all_with_subjects() -> List[Dict[str, Any]]:
        """
        获取所有题型及其关联的学科列表

        Returns:
            题型列表，每个题型包含 en_name, zh_name, subjects 字段
            subjects 为逗号分隔的字符串解析为列表
        """
        conn = QuestionTypeStore.get_connection()
        try:
            # 获取所有启用的题型
            cursor = conn.execute(
                "SELECT * FROM question_types WHERE is_active = 1 ORDER BY id"
            )
            rows = cursor.fetchall()

            result = []
            for row in rows:
                qt_dict = dict(row)

                # 从 subjects 字段解析学科列表（逗号分隔）
                subjects_str = qt_dict.get('subjects', 'math,chinese,english')
                subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]

                # 如果为空，使用默认值
                if not subjects:
                    subjects = ['math', 'chinese', 'english']

                result.append({
                    "id": qt_dict['id'],
                    "en_name": qt_dict['en_name'],
                    "zh_name": qt_dict['zh_name'],
                    "subjects": subjects,
                })

            return result
        finally:
            conn.close()
