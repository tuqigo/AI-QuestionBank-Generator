"""
数据库辅助工具类

提供便捷的数据库查询和更新方法，用于快速配置和调试任务。
典型使用场景：配置题目模板、批量更新数据等。
"""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from config import DB_PATH


def _get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH), isolation_level=None)
    conn.execute("PRAGMA encoding = 'UTF-8'")
    conn.row_factory = sqlite3.Row
    return conn


class DbHelper:
    """数据库辅助类 - 用于快速查询和更新"""

    # ==================== 通用查询方法 ====================

    @staticmethod
    def query_one(table: str, where: Dict[str, Any], columns: str = "*") -> Optional[sqlite3.Row]:
        """
        查询单条记录

        Args:
            table: 表名
            where: WHERE 条件字典，如 {"id": 14}
            columns: 要查询的列，默认 "*"

        Returns:
            sqlite3.Row 对象或 None

        Example:
            >>> DbHelper.query_one("question_templates", {"id": 14})
            >>> DbHelper.query_one("knowledge_points", {"id": 1}, "id, name, subject_code")
        """
        conn = _get_connection()
        try:
            conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
            values = list(where.values())
            cursor = conn.execute(
                f"SELECT {columns} FROM {table} WHERE {conditions} LIMIT 1",
                values
            )
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def query_all(table: str, where: Optional[Dict[str, Any]] = None,
                  columns: str = "*", order_by: Optional[str] = None) -> List[sqlite3.Row]:
        """
        查询多条记录

        Args:
            table: 表名
            where: WHERE 条件字典（可选）
            columns: 要查询的列，默认 "*"
            order_by: ORDER BY 子句（可选）

        Returns:
            sqlite3.Row 列表

        Example:
            >>> DbHelper.query_all("question_templates", {"grade": "grade2"})
            >>> DbHelper.query_all("knowledge_points", {"subject_code": "math"}, "id, name", "sort_order")
        """
        conn = _get_connection()
        try:
            if where:
                conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
                values = list(where.values())
                sql = f"SELECT {columns} FROM {table} WHERE {conditions}"
                if order_by:
                    sql += f" ORDER BY {order_by}"
                cursor = conn.execute(sql, values)
            else:
                sql = f"SELECT {columns} FROM {table}"
                if order_by:
                    sql += f" ORDER BY {order_by}"
                cursor = conn.execute(sql)
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def query_sql(sql: str, params: Optional[tuple] = None) -> List[sqlite3.Row]:
        """
        执行自定义 SQL 查询

        Args:
            sql: SQL 语句
            params: 参数元组（可选）

        Returns:
            sqlite3.Row 列表

        Example:
            >>> DbHelper.query_sql("SELECT * FROM question_templates WHERE id = ?", (14,))
        """
        conn = _get_connection()
        try:
            cursor = conn.execute(sql, params or ())
            return cursor.fetchall()
        finally:
            conn.close()

    # ==================== 通用更新方法 ====================

    @staticmethod
    def update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        更新记录

        Args:
            table: 表名
            data: 要更新的数据字典
            where: WHERE 条件字典

        Returns:
            受影响的行数

        Example:
            >>> DbHelper.update("question_templates", {"is_active": 1, "template_pattern": "{a}+{b}"}, {"id": 14})
        """
        conn = _get_connection()
        try:
            sets = ", ".join([f"{k} = ?" for k in data.keys()])
            where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
            values = list(data.values()) + list(where.values())
            cursor = conn.execute(
                f"UPDATE {table} SET {sets} WHERE {where_clause}",
                values
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    @staticmethod
    def update_json_column(table: str, column: str, data: Dict[str, Any],
                           where: Dict[str, Any]) -> int:
        """
        更新 JSON 列（将数据序列化为 JSON 字符串）

        Args:
            table: 表名
            column: JSON 列名
            data: 要存储的字典数据
            where: WHERE 条件字典

        Returns:
            受影响的行数

        Example:
            >>> DbHelper.update_json_column("question_templates", "variables_config", {"num": {"min": 10}}, {"id": 14})
        """
        conn = _get_connection()
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
            values = [json_str] + list(where.values())
            cursor = conn.execute(
                f"UPDATE {table} SET {column} = ? WHERE {where_clause}",
                values
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> int:
        """
        插入记录

        Args:
            table: 表名
            data: 要插入的数据字典

        Returns:
            新记录的 ID

        Example:
            >>> DbHelper.insert("knowledge_points", {"name": "新知识点", "subject_code": "math"})
        """
        conn = _get_connection()
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data.keys()])
            values = list(data.values())
            cursor = conn.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                values
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    # ==================== 题目模板专用方法 ====================

    @staticmethod
    def get_template(template_id: int) -> Optional[sqlite3.Row]:
        """获取题目模板记录"""
        return DbHelper.query_one("question_templates", {"id": template_id})

    @staticmethod
    def update_template(template_id: int, **kwargs) -> int:
        """
        更新题目模板

        Args:
            template_id: 模板 ID
            **kwargs: 要更新的字段

        Example:
            >>> DbHelper.update_template(14, is_active=1, generator_module="mixed_addition_subtraction")
        """
        return DbHelper.update("question_templates", kwargs, {"id": template_id})

    @staticmethod
    def update_template_variables(template_id: int, variables_config: Dict[str, Any]) -> int:
        """
        更新模板的 variables_config 字段（自动序列化为 JSON）

        Args:
            template_id: 模板 ID
            variables_config: 配置字典

        Returns:
            受影响的行数

        Example:
            >>> DbHelper.update_template_variables(14, {"num": {"min": 10, "max": 99}, "ensure_no_carrying": True})
        """
        return DbHelper.update_json_column("question_templates", "variables_config",
                                            variables_config, {"id": template_id})

    @staticmethod
    def get_knowledge_point(kp_id: int) -> Optional[sqlite3.Row]:
        """获取知识点记录"""
        return DbHelper.query_one("knowledge_points", {"id": kp_id})

    @staticmethod
    def get_knowledge_points_by_grade(grade_code: str, subject_code: str = "math") -> List[sqlite3.Row]:
        """
        根据年级获取知识点列表

        Args:
            grade_code: 年级代码，如 "grade2"
            subject_code: 学科代码，默认 "math"

        Returns:
            知识点列表
        """
        return DbHelper.query_all(
            "knowledge_points",
            {"grade_code": grade_code, "subject_code": subject_code},
            order_by="sort_order"
        )


# ==================== 便捷函数 ====================

def query_one(table: str, where: Dict[str, Any], columns: str = "*") -> Optional[sqlite3.Row]:
    """便捷函数：查询单条记录"""
    return DbHelper.query_one(table, where, columns)


def query_all(table: str, where: Optional[Dict[str, Any]] = None,
              columns: str = "*", order_by: Optional[str] = None) -> List[sqlite3.Row]:
    """便捷函数：查询多条记录"""
    return DbHelper.query_all(table, where, columns, order_by)


def update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
    """便捷函数：更新记录"""
    return DbHelper.update(table, data, where)


def update_json_column(table: str, column: str, data: Dict[str, Any],
                       where: Dict[str, Any]) -> int:
    """便捷函数：更新 JSON 列"""
    return DbHelper.update_json_column(table, column, data, where)
