"""
题目模板存储服务
负责模板的 CRUD 操作
"""
import sqlite3
import json
from typing import Optional, List
from datetime import datetime, timezone

from models.question_template import (
    QuestionTemplate,
    QuestionTemplateListItem,
)
from utils.logger import api_logger
from config import DB_PATH


def _utc_now() -> str:
    """返回 UTC 时间字符串"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==================== 创建/更新/删除 ====================

def create_template(
    name: str,
    subject: str,
    grade: str,
    semester: str,
    textbook_version: str,
    question_type: str,
    template_pattern: str,
    variables_config: str,  # JSON 字符串格式
    example: Optional[str] = None,
    sort_order: int = 0,
    is_active: bool = True,
) -> int:
    """
    创建新模板
    返回新模板的 ID
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO question_templates
            (name, subject, grade, semester, textbook_version, question_type, template_pattern,
             variables_config, example, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, subject, grade, semester, textbook_version, question_type, template_pattern,
             variables_config, example, sort_order, 1 if is_active else 0)
        )
        conn.commit()
        template_id = cursor.lastrowid
        api_logger.info(f"模板创建成功：id={template_id}, name={name}")
        return template_id
    except Exception as e:
        api_logger.error(f"创建模板失败：{e}")
        raise
    finally:
        conn.close()


def update_template(
    template_id: int,
    name: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    semester: Optional[str] = None,
    textbook_version: Optional[str] = None,
    template_pattern: Optional[str] = None,
    variables_config: Optional[str] = None,  # JSON 字符串格式
    example: Optional[str] = None,
    sort_order: Optional[int] = None,
    is_active: Optional[bool] = None,
    question_type: Optional[str] = None,
    generator_module: Optional[str] = None,
) -> bool:
    """
    更新模板
    只更新提供的字段
    """
    conn = _get_connection()
    try:
        updates = []
        values = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if subject is not None:
            updates.append("subject = ?")
            values.append(subject)
        if grade is not None:
            updates.append("grade = ?")
            values.append(grade)
        if semester is not None:
            updates.append("semester = ?")
            values.append(semester)
        if textbook_version is not None:
            updates.append("textbook_version = ?")
            values.append(textbook_version)
        if template_pattern is not None:
            updates.append("template_pattern = ?")
            values.append(template_pattern)
        if variables_config is not None:
            updates.append("variables_config = ?")
            values.append(variables_config)  # 已经是 JSON 字符串，无需转换
        if example is not None:
            updates.append("example = ?")
            values.append(example)
        if sort_order is not None:
            updates.append("sort_order = ?")
            values.append(sort_order)
        if is_active is not None:
            updates.append("is_active = ?")
            values.append(1 if is_active else 0)
        if question_type is not None:
            updates.append("question_type = ?")
            values.append(question_type)
        if generator_module is not None:
            updates.append("generator_module = ?")
            values.append(generator_module)

        if not updates:
            return False

        updates.append("updated_at = ?")
        values.append(_utc_now())
        values.append(template_id)

        sql = f"UPDATE question_templates SET {', '.join(updates)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()

        if cursor.rowcount > 0:
            api_logger.info(f"模板更新成功：id={template_id}")
            return True
        else:
            api_logger.warning(f"模板更新失败：记录不存在 id={template_id}")
            return False
    except Exception as e:
        api_logger.error(f"更新模板失败：{e}")
        raise
    finally:
        conn.close()


def delete_template(template_id: int) -> bool:
    """
    删除模板（物理删除）
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM question_templates WHERE id = ?",
            (template_id,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            api_logger.info(f"模板删除成功：id={template_id}")
            return True
        else:
            api_logger.warning(f"模板删除失败：记录不存在 id={template_id}")
            return False
    except Exception as e:
        api_logger.error(f"删除模板失败：{e}")
        raise
    finally:
        conn.close()


# ==================== 查询 ====================

def get_template_by_id(template_id: int) -> Optional[QuestionTemplate]:
    """
    根据 ID 获取模板
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, name, subject, grade, semester, textbook_version, question_type, template_pattern,
                   variables_config, example, generator_module, sort_order, is_active,
                   created_at, updated_at
            FROM question_templates
            WHERE id = ?
            """,
            (template_id,)
        )
        row = cursor.fetchone()

        if row:
            return _row_to_template(row)
        return None
    except Exception as e:
        api_logger.error(f"获取模板失败：{e}")
        raise
    finally:
        conn.close()


def get_all_templates() -> List[QuestionTemplate]:
    """
    获取所有启用的模板（按 sort_order 排序）
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, name, subject, grade, semester, textbook_version, question_type, template_pattern,
                   variables_config, example, generator_module, sort_order, is_active,
                   created_at, updated_at
            FROM question_templates
            WHERE is_active = 1
            ORDER BY sort_order ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        return [_row_to_template(row) for row in rows]
    except Exception as e:
        api_logger.error(f"获取模板列表失败：{e}")
        raise
    finally:
        conn.close()


def get_templates_by_grade(subject: str, grade: str) -> List[QuestionTemplate]:
    """
    根据学科和年级获取模板
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, name, subject, grade, semester, textbook_version, question_type, template_pattern,
                   variables_config, example, generator_module, sort_order, is_active,
                   created_at, updated_at
            FROM question_templates
            WHERE subject = ? AND grade = ? AND is_active = 1
            ORDER BY sort_order ASC, id ASC
            """,
            (subject, grade)
        )
        rows = cursor.fetchall()
        return [_row_to_template(row) for row in rows]
    except Exception as e:
        api_logger.error(f"获取模板列表失败：{e}")
        raise
    finally:
        conn.close()


def get_template_list_items() -> List[QuestionTemplateListItem]:
    """
    获取模板列表项（精简版，用于前端下拉选择）
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, name, subject, grade, semester, textbook_version, question_type, example, sort_order
            FROM question_templates
            WHERE is_active = 1
            ORDER BY sort_order ASC, id ASC
            """
        )
        rows = cursor.fetchall()
        return [_row_to_list_item(row) for row in rows]
    except Exception as e:
        api_logger.error(f"获取模板列表失败：{e}")
        raise
    finally:
        conn.close()


# ==================== 使用记录 ====================

def log_template_usage(
    template_id: int,
    user_id: int,
    record_id: int,
    generated_params: dict,
) -> int:
    """
    记录模板使用情况
    返回记录 ID
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO template_usage_logs
            (template_id, user_id, record_id, generated_params)
            VALUES (?, ?, ?, ?)
            """,
            (template_id, user_id, record_id,
             json.dumps(generated_params, ensure_ascii=False))
        )
        conn.commit()
        log_id = cursor.lastrowid
        api_logger.info(f"模板使用记录创建成功：id={log_id}")
        return log_id
    except Exception as e:
        api_logger.error(f"记录模板使用失败：{e}")
        raise
    finally:
        conn.close()


# ==================== 辅助函数 ====================

def _row_to_template(row: sqlite3.Row) -> QuestionTemplate:
    """将数据库行转换为 QuestionTemplate 对象"""
    return QuestionTemplate(
        id=row["id"],
        name=row["name"],
        subject=row["subject"],
        grade=row["grade"],
        semester=row["semester"],
        textbook_version=row["textbook_version"],
        question_type=row["question_type"],
        template_pattern=row["template_pattern"],
        variables_config=json.loads(row["variables_config"]),
        example=row["example"],
        generator_module=row["generator_module"],
        sort_order=row["sort_order"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


def _row_to_list_item(row: sqlite3.Row) -> QuestionTemplateListItem:
    """将数据库行转换为 QuestionTemplateListItem 对象"""
    return QuestionTemplateListItem(
        id=row["id"],
        name=row["name"],
        subject=row["subject"],
        grade=row["grade"],
        semester=row["semester"],
        textbook_version=row["textbook_version"],
        question_type=row["question_type"],
        example=row["example"],
        sort_order=row["sort_order"]
    )
