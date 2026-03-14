"""AI 生成记录存储 - SQLite"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime, timezone

from models.ai_generation_record import AiGenerationRecordCreate, AiGenerationRecordResponse, AiGenerationRecordFilter
from utils.logger import user_logger

# 数据库文件路径（与用户表同一个数据库）
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def _utc_now() -> str:
    """返回 UTC 时间字符串（带 Z 后缀）"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_record(record: AiGenerationRecordCreate) -> int:
    """创建 AI 生成记录，返回新记录的 ID"""
    user_logger.info(f"创建 AI 生成记录：user_id={record.user_id}, prompt_type={record.prompt_type}, success={record.success}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO ai_generation_records
            (user_id, prompt, prompt_type, success, duration, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (record.user_id, record.prompt, record.prompt_type,
             1 if record.success else 0, record.duration, record.error_message, _utc_now())
        )
        conn.commit()
        record_id = cursor.lastrowid
        user_logger.info(f"AI 生成记录创建成功：id={record_id}")
        return record_id
    except Exception as e:
        user_logger.error(f"创建 AI 生成记录失败：{e}")
        raise
    finally:
        conn.close()


def get_record_by_id(record_id: int) -> Optional[AiGenerationRecordResponse]:
    """根据 ID 获取记录"""
    user_logger.info(f"获取 AI 生成记录：id={record_id}")
    conn = _get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT r.id, r.user_id, r.prompt, r.prompt_type, r.success, r.duration, r.error_message, r.created_at,
                   u.email as user_email
            FROM ai_generation_records r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.id = ?
            """,
            (record_id,)
        )
        row = cursor.fetchone()
        if row:
            return _row_to_response(row)
        return None
    finally:
        conn.close()


def get_records(
    filter: AiGenerationRecordFilter,
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[AiGenerationRecordResponse], int, bool]:
    """获取 AI 生成记录列表（分页、筛选）
    返回：(记录列表，总数，是否有更多)
    """
    user_logger.info(f"获取 AI 生成记录列表：filter={filter}, page={page}, page_size={page_size}")
    conn = _get_connection()
    try:
        # 构建筛选条件
        where_clauses = []
        params = []

        if filter.user_id:
            where_clauses.append("r.user_id = ?")
            params.append(filter.user_id)

        if filter.success is not None:
            where_clauses.append("r.success = ?")
            params.append(1 if filter.success else 0)

        if filter.prompt_type:
            where_clauses.append("r.prompt_type = ?")
            params.append(filter.prompt_type)

        if filter.date_from:
            where_clauses.append("date(r.created_at) >= ?")
            params.append(filter.date_from)

        if filter.date_to:
            where_clauses.append("date(r.created_at) <= ?")
            params.append(filter.date_to)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        # 计算总数
        count_sql = f"""
            SELECT COUNT(*) as count
            FROM ai_generation_records r
            {where_sql}
        """
        count_row = conn.execute(count_sql, params).fetchone()
        total = count_row["count"] if count_row else 0

        # 计算分页
        offset = (page - 1) * page_size

        # 查询数据
        data_sql = f"""
            SELECT r.id, r.user_id, r.prompt, r.prompt_type, r.success, r.duration, r.error_message, r.created_at,
                   u.email as user_email
            FROM ai_generation_records r
            LEFT JOIN users u ON r.user_id = u.id
            {where_sql}
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(data_sql, params + [page_size, offset]).fetchall()

        results = [_row_to_response(row) for row in rows]
        has_more = len(results) < total

        user_logger.info(f"AI 生成记录查询成功：total={total}, returned={len(results)}")
        return results, total, has_more
    except Exception as e:
        user_logger.error(f"获取 AI 生成记录列表失败：{e}")
        raise
    finally:
        conn.close()


def get_user_records(
    user_id: int,
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[AiGenerationRecordResponse], int, bool]:
    """获取指定用户的 AI 生成记录列表"""
    filter = AiGenerationRecordFilter(user_id=user_id)
    return get_records(filter, page, page_size)


def get_recent_failed_records(limit: int = 50) -> List[AiGenerationRecordResponse]:
    """获取最近的失败记录（用于监控）"""
    user_logger.info(f"获取最近的失败记录：limit={limit}")
    conn = _get_connection()
    try:
        rows = conn.execute(
            """
            SELECT r.id, r.user_id, r.prompt, r.prompt_type, r.success, r.duration, r.error_message, r.created_at,
                   u.email as user_email
            FROM ai_generation_records r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.success = 0
            ORDER BY r.created_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [_row_to_response(row) for row in rows]
    finally:
        conn.close()


def get_statistics_by_user(user_id: int) -> dict:
    """获取用户的统计信息"""
    user_logger.info(f"获取用户统计信息：user_id={user_id}")
    conn = _get_connection()
    try:
        # 总数
        total_row = conn.execute(
            "SELECT COUNT(*) as count FROM ai_generation_records WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        total = total_row["count"] if total_row else 0

        # 成功数
        success_row = conn.execute(
            "SELECT COUNT(*) as count FROM ai_generation_records WHERE user_id = ? AND success = 1",
            (user_id,)
        ).fetchone()
        success_count = success_row["count"] if success_row else 0

        # 失败数
        failed_row = conn.execute(
            "SELECT COUNT(*) as count FROM ai_generation_records WHERE user_id = ? AND success = 0",
            (user_id,)
        ).fetchone()
        failed_count = failed_row["count"] if failed_row else 0

        # 平均耗时（仅成功记录）
        avg_row = conn.execute(
            "SELECT AVG(duration) as avg_duration FROM ai_generation_records WHERE user_id = ? AND success = 1",
            (user_id,)
        ).fetchone()
        avg_duration = round(avg_row["avg_duration"], 2) if avg_row and avg_row["avg_duration"] else 0

        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "avg_duration": avg_duration
        }
    finally:
        conn.close()


def _row_to_response(row: sqlite3.Row) -> AiGenerationRecordResponse:
    """将数据库行转换为响应对象"""
    return AiGenerationRecordResponse(
        id=row["id"],
        user_id=row["user_id"],
        user_email=row["user_email"] or "unknown",
        prompt=row["prompt"],
        prompt_type=row["prompt_type"],
        success=bool(row["success"]),
        duration=row["duration"],
        error_message=row["error_message"],
        created_at=row["created_at"]
    )
