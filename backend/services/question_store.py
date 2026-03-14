"""
题目存储服务
负责题目的批量插入、查询等操作
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from utils.logger import api_logger
from utils.short_id import generate_short_id

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def _utc_now() -> str:
    """返回 UTC 时间字符串（带 Z 后缀）"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _generate_unique_short_id(conn: sqlite3.Connection) -> str:
    """生成唯一的 short_id（检查冲突）"""
    max_attempts = 10
    for _ in range(max_attempts):
        short_id = generate_short_id()
        # 检查是否已存在
        row = conn.execute(
            "SELECT 1 FROM questions WHERE short_id = ?",
            (short_id,)
        ).fetchone()
        if not row:
            return short_id
    raise RuntimeError("生成 short_id 失败：多次尝试后仍冲突")


class QuestionData:
    """题目数据结构"""
    def __init__(
        self,
        record_id: int,
        question_index: int,
        question_type: str,
        stem: str,
        knowledge_points: List[str],
        options: Optional[List[str]] = None,
        passage: Optional[str] = None,
        sub_questions: Optional[List[Dict[str, Any]]] = None,
        answer_blanks: Optional[int] = None,
        rows_to_answer: Optional[int] = None,
        answer_text: Optional[str] = None
    ):
        self.record_id = record_id
        self.question_index = question_index
        self.type = question_type
        self.stem = stem
        self.knowledge_points = knowledge_points
        self.options = options
        self.passages = passage
        self.sub_questions = sub_questions
        self.answer_blanks = answer_blanks
        self.rows_to_answer = rows_to_answer
        self.answer_text = answer_text


def batch_insert_questions(
    record_id: int,
    questions: List[Dict[str, Any]]
) -> List[Tuple[int, str]]:
    """
    批量插入题目到数据库

    Args:
        record_id: 所属试卷 ID
        questions: 清洗后的题目列表

    Returns:
        [(question_id, short_id), ...] 列表
    """
    api_logger.info(f"批量插入题目：record_id={record_id}, 题目数={len(questions)}")
    conn = _get_connection()
    try:
        results = []
        for q in questions:
            # 生成 short_id
            short_id = _generate_unique_short_id(conn)

            # 将列表/字典序列化为 JSON 字符串
            options_json = json.dumps(q.get("options"), ensure_ascii=False) if q.get("options") else None
            passage_json = json.dumps(q.get("passage"), ensure_ascii=False) if q.get("passage") else None
            sub_questions_json = json.dumps(q.get("sub_questions"), ensure_ascii=False) if q.get("sub_questions") else None
            knowledge_points_json = json.dumps(q.get("knowledge_points"), ensure_ascii=False)

            cursor = conn.execute(
                """
                INSERT INTO questions
                (short_id, record_id, question_index, type, stem, options, passage,
                 sub_questions, knowledge_points, answer_blanks, rows_to_answer,
                 answer_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    short_id,
                    record_id,
                    q.get("_index", q.get("question_index", 1)),
                    q.get("type", ""),
                    q.get("stem", ""),
                    options_json,
                    passage_json,
                    sub_questions_json,
                    knowledge_points_json,
                    q.get("answer_blanks"),
                    q.get("rows_to_answer"),
                    q.get("answer_text"),
                    _utc_now()
                )
            )
            conn.commit()
            question_id = cursor.lastrowid
            results.append((question_id, short_id))
            api_logger.info(f"题目插入成功：id={question_id}, short_id={short_id}, type={q.get('type')}")

        api_logger.info(f"批量插入完成：成功={len(results)}")
        return results

    except Exception as e:
        api_logger.error(f"批量插入题目失败：{e}")
        api_logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise
    finally:
        conn.close()


def get_questions_by_record_id(record_id: int) -> List[Dict[str, Any]]:
    """
    根据试卷 ID 获取所有题目

    Args:
        record_id: 试卷 ID

    Returns:
        题目列表，按 question_index 排序
    """
    api_logger.info(f"获取试卷题目：record_id={record_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, short_id, record_id, question_index, type, stem,
                   options, passage, sub_questions, knowledge_points,
                   answer_blanks, rows_to_answer, answer_text, created_at
            FROM questions
            WHERE record_id = ?
            ORDER BY question_index ASC
            """,
            (record_id,)
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            question = {
                "id": row["id"],
                "short_id": row["short_id"],
                "record_id": row["record_id"],
                "question_index": row["question_index"],
                "type": row["type"],
                "stem": row["stem"],
                "knowledge_points": json.loads(row["knowledge_points"]) if row["knowledge_points"] else [],
                "answer_blanks": row["answer_blanks"],
                "rows_to_answer": row["rows_to_answer"],
                "answer_text": row["answer_text"],
                "created_at": row["created_at"]
            }

            # 可选字段
            if row["options"]:
                question["options"] = json.loads(row["options"])
            if row["passage"]:
                question["passage"] = json.loads(row["passage"])
            if row["sub_questions"]:
                question["sub_questions"] = json.loads(row["sub_questions"])

            results.append(question)

        api_logger.info(f"获取试卷题目成功：record_id={record_id}, 题目数={len(results)}")
        return results

    except Exception as e:
        api_logger.error(f"获取试卷题目失败：{e}")
        raise
    finally:
        conn.close()


def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    """
    根据题目 ID 获取单道题目

    Args:
        question_id: 题目 ID

    Returns:
        题目数据，不存在返回 None
    """
    api_logger.info(f"获取题目：id={question_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, short_id, record_id, question_index, type, stem,
                   options, passage, sub_questions, knowledge_points,
                   answer_blanks, rows_to_answer, answer_text, created_at
            FROM questions
            WHERE id = ?
            """,
            (question_id,)
        )
        row = cursor.fetchone()

        if not row:
            api_logger.warning(f"题目不存在：id={question_id}")
            return None

        question = {
            "id": row["id"],
            "short_id": row["short_id"],
            "record_id": row["record_id"],
            "question_index": row["question_index"],
            "type": row["type"],
            "stem": row["stem"],
            "knowledge_points": json.loads(row["knowledge_points"]) if row["knowledge_points"] else [],
            "answer_blanks": row["answer_blanks"],
            "rows_to_answer": row["rows_to_answer"],
            "answer_text": row["answer_text"],
            "created_at": row["created_at"]
        }

        # 可选字段
        if row["options"]:
            question["options"] = json.loads(row["options"])
        if row["passage"]:
            question["passage"] = json.loads(row["passage"])
        if row["sub_questions"]:
            question["sub_questions"] = json.loads(row["sub_questions"])

        api_logger.info(f"获取题目成功：id={question_id}, type={row['type']}")
        return question

    except Exception as e:
        api_logger.error(f"获取题目失败：{e}")
        raise
    finally:
        conn.close()


def get_question_answer(question_id: int) -> Optional[Dict[str, Any]]:
    """
    获取单道题目的答案

    Args:
        question_id: 题目 ID

    Returns:
        答案数据，包含 type, answer_text, answer_blanks, rows_to_answer
    """
    api_logger.info(f"获取题目答案：id={question_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, type, answer_text, answer_blanks, rows_to_answer
            FROM questions
            WHERE id = ?
            """,
            (question_id,)
        )
        row = cursor.fetchone()

        if not row:
            api_logger.warning(f"题目不存在：id={question_id}")
            return None

        return {
            "question_id": row["id"],
            "type": row["type"],
            "answer_text": row["answer_text"],
            "answer_blanks": row["answer_blanks"],
            "rows_to_answer": row["rows_to_answer"]
        }

    except Exception as e:
        api_logger.error(f"获取题目答案失败：{e}")
        raise
    finally:
        conn.close()


def get_answers_by_record_id(record_id: int) -> List[Dict[str, Any]]:
    """
    根据试卷 ID 获取所有题目的答案

    Args:
        record_id: 试卷 ID

    Returns:
        答案列表，按 question_index 排序
    """
    api_logger.info(f"获取整卷答案：record_id={record_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, question_index, type, answer_text, answer_blanks, rows_to_answer
            FROM questions
            WHERE record_id = ?
            ORDER BY question_index ASC
            """,
            (record_id,)
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "question_id": row["id"],
                "question_index": row["question_index"],
                "type": row["type"],
                "answer_text": row["answer_text"],
                "answer_blanks": row["answer_blanks"],
                "rows_to_answer": row["rows_to_answer"]
            })

        api_logger.info(f"获取整卷答案成功：record_id={record_id}, 题目数={len(results)}")
        return results

    except Exception as e:
        api_logger.error(f"获取整卷答案失败：{e}")
        raise
    finally:
        conn.close()


def get_question_by_short_id(short_id: str) -> Optional[Dict[str, Any]]:
    """
    根据 short_id 获取题目

    Args:
        short_id: 题目短 ID

    Returns:
        题目数据，不存在返回 None
    """
    api_logger.info(f"获取题目：short_id={short_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, short_id, record_id, question_index, type, stem,
                   options, passage, sub_questions, knowledge_points,
                   answer_blanks, rows_to_answer, answer_text, created_at
            FROM questions
            WHERE short_id = ?
            """,
            (short_id,)
        )
        row = cursor.fetchone()

        if not row:
            api_logger.warning(f"题目不存在：short_id={short_id}")
            return None

        question = {
            "id": row["id"],
            "short_id": row["short_id"],
            "record_id": row["record_id"],
            "question_index": row["question_index"],
            "type": row["type"],
            "stem": row["stem"],
            "knowledge_points": json.loads(row["knowledge_points"]) if row["knowledge_points"] else [],
            "answer_blanks": row["answer_blanks"],
            "rows_to_answer": row["rows_to_answer"],
            "answer_text": row["answer_text"],
            "created_at": row["created_at"]
        }

        # 可选字段
        if row["options"]:
            question["options"] = json.loads(row["options"])
        if row["passage"]:
            question["passage"] = json.loads(row["passage"])
        if row["sub_questions"]:
            question["sub_questions"] = json.loads(row["sub_questions"])

        api_logger.info(f"获取题目成功：short_id={short_id}, type={row['type']}")
        return question

    except Exception as e:
        api_logger.error(f"获取题目失败：{e}")
        raise
    finally:
        conn.close()
