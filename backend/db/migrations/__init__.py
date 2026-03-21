"""
数据库迁移管理器

功能：
1. 扫描 migrations 目录获取待执行的迁移脚本
2. 通过 schema_migrations 表记录已执行的迁移
3. 只执行未记录的迁移脚本，保证幂等性
4. 完善的异常处理和事务支持
"""

import sqlite3
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
import logging

from config import DB_PATH

# 配置日志
logger = logging.getLogger(__name__)

# 迁移文件目录
MIGRATIONS_DIR = Path(__file__).parent


class MigrationError(Exception):
    """迁移异常基类"""
    pass


class MigrationChecksumError(MigrationError):
    """校验和错误"""
    pass


class MigrationExecutor:
    """迁移执行器"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化迁移执行器

        Args:
            db_path: 数据库文件路径，默认使用 config 中的 DB_PATH
        """
        self.db_path = db_path or DB_PATH
        self._ensure_db_directory()

    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _calculate_checksum(self, content: str) -> str:
        """计算 SQL 内容的 SHA-256 校验和"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _ensure_migrations_table(self, conn: sqlite3.Connection):
        """确保 schema_migrations 表存在"""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT (datetime('now')),
                checksum TEXT,
                status TEXT DEFAULT 'success'
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_schema_migrations_version
            ON schema_migrations(version)
        """)
        conn.commit()

    def _get_executed_migrations(self, conn: sqlite3.Connection) -> List[str]:
        """获取已执行的迁移版本列表"""
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_migrations WHERE status = 'success' ORDER BY version")
        return [row['version'] for row in cursor.fetchall()]

    def _record_migration(
        self,
        conn: sqlite3.Connection,
        version: str,
        filename: str,
        checksum: str
    ):
        """记录迁移执行成功"""
        cursor = conn.cursor()
        # 先检查是否已存在该版本的记录
        cursor.execute("SELECT id FROM schema_migrations WHERE version = ?", (version,))
        if cursor.fetchone() is not None:
            logger.warning(f"迁移记录已存在，跳过：{filename} (version: {version})")
            return

        cursor.execute("""
            INSERT OR IGNORE INTO schema_migrations (version, filename, checksum, status)
            VALUES (?, ?, ?, 'success')
        """, (version, filename, checksum))

    def _get_migration_files(self) -> List[Path]:
        """
        获取所有迁移文件，按版本号排序

        迁移文件命名规则：NNN_description.sql
        - NNN: 3 位数字版本号（001, 002, ...）
        - description: 描述性名称
        """
        if not MIGRATIONS_DIR.exists():
            logger.warning(f"迁移目录不存在：{MIGRATIONS_DIR}")
            return []

        migration_files = []
        for file in MIGRATIONS_DIR.glob("*.sql"):
            # 跳过以 000_ 开头的迁移表创建脚本（特殊处理）
            if file.name.startswith("000_"):
                migration_files.append(file)
                continue

            # 验证文件名格式：NNN_description.sql
            match = re.match(r"^(\d{3})_.+\.sql$", file.name)
            if match:
                migration_files.append(file)
            else:
                logger.warning(f"跳过不符合命名规范的文件：{file.name}")

        # 按文件名排序（即按版本号排序）
        return sorted(migration_files, key=lambda x: x.name)

    def _parse_version(self, filename: str) -> str:
        """从文件名解析版本号"""
        match = re.match(r"^(\d{3})_", filename)
        if match:
            return match.group(1)
        raise MigrationError(f"无法从文件名解析版本号：{filename}")

    def _execute_migration(
        self,
        conn: sqlite3.Connection,
        filepath: Path,
        version: str
    ):
        """
        执行单个迁移文件

        Args:
            conn: 数据库连接
            filepath: 迁移文件路径
            version: 版本号
        """
        # 读取迁移文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 计算校验和
        checksum = self._calculate_checksum(sql_content)

        # 执行迁移 SQL
        cursor = conn.cursor()
        cursor.executescript(sql_content)

        # 记录迁移执行成功
        self._record_migration(conn, version, filepath.name, checksum)

        logger.info(f"执行迁移：{filepath.name} (version: {version})")

    def migrate(self) -> List[str]:
        """
        执行所有待执行的迁移

        Returns:
            已执行的迁移文件名列表

        Raises:
            MigrationError: 迁移执行失败
            MigrationChecksumError: 校验和错误（如果未来需要校验）
        """
        executed = []
        conn = None

        try:
            # 确保数据库目录存在
            self._ensure_db_directory()

            # 连接数据库
            conn = self._get_connection()

            # 确保迁移表存在（首先执行 000_迁移）
            self._ensure_migrations_table(conn)

            # 获取已执行的迁移
            executed_versions = set(self._get_executed_migrations(conn))

            # 获取所有迁移文件
            migration_files = self._get_migration_files()

            if not migration_files:
                logger.info("没有找到迁移文件")
                return executed

            # 执行待执行的迁移
            for filepath in migration_files:
                version = self._parse_version(filepath.name)

                # 跳过已执行的迁移
                if version in executed_versions:
                    logger.debug(f"迁移已执行，跳过：{filepath.name}")
                    continue

                try:
                    # 执行迁移（在事务中）
                    with conn:
                        self._execute_migration(conn, filepath, version)
                    executed.append(filepath.name)

                except sqlite3.Error as e:
                    # 记录失败的迁移
                    cursor = conn.cursor()
                    # 先检查是否已存在该版本的记录
                    cursor.execute("SELECT id FROM schema_migrations WHERE version = ?", (version,))
                    if cursor.fetchone() is None:
                        cursor.execute("""
                            INSERT OR IGNORE INTO schema_migrations (version, filename, checksum, status)
                            VALUES (?, ?, ?, 'failed')
                        """, (version, filepath.name, self._calculate_checksum(filepath.read_text(encoding='utf-8'))))
                        conn.commit()

                    error_msg = f"迁移执行失败 [{filepath.name}]: {e}"
                    logger.error(error_msg)
                    raise MigrationError(error_msg) from e

            if executed:
                logger.info(f"迁移完成，执行了 {len(executed)} 个迁移：{executed}")
            else:
                logger.info("数据库已是最新版本，无需迁移")

            return executed

        except Exception as e:
            logger.error(f"迁移过程中发生错误：{e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_migration_history(self) -> List[dict]:
        """
        获取迁移历史记录

        Returns:
            迁移历史记录列表，包含版本、文件名、执行时间、状态
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, filename, executed_at, checksum, status
                FROM schema_migrations
                ORDER BY version
            """)

            history = []
            for row in cursor.fetchall():
                history.append({
                    'version': row['version'],
                    'filename': row['filename'],
                    'executed_at': row['executed_at'],
                    'checksum': row['checksum'],
                    'status': row['status']
                })
            return history
        finally:
            if conn:
                conn.close()

    def get_pending_migrations(self) -> List[str]:
        """
        获取待执行的迁移文件列表

        Returns:
            待执行的迁移文件名列表
        """
        conn = None
        try:
            conn = self._get_connection()
            self._ensure_migrations_table(conn)
            executed_versions = set(self._get_executed_migrations(conn))

            pending = []
            for filepath in self._get_migration_files():
                version = self._parse_version(filepath.name)
                if version not in executed_versions:
                    pending.append(filepath.name)

            return pending
        finally:
            if conn:
                conn.close()

    def rollback(self, target_version: str) -> bool:
        """
        回滚到指定版本（仅标记为回滚，不执行实际回滚 SQL）

        注意：SQLite 迁移通常不支持自动回滚，需要手动编写回滚脚本

        Args:
            target_version: 目标版本号

        Returns:
            是否成功回滚
        """
        logger.warning(f"回滚功能暂未完全实现，目标版本：{target_version}")
        # TODO: 实现回滚功能需要：
        # 1. 每个迁移文件配备对应的回滚 SQL
        # 2. 或者支持从 schema_migrations 删除记录
        return False


# 便捷函数
def run_migrations() -> List[str]:
    """
    执行数据库迁移

    Returns:
        已执行的迁移文件名列表
    """
    executor = MigrationExecutor()
    return executor.migrate()


def get_migration_status() -> dict:
    """
    获取迁移状态摘要

    Returns:
        包含迁移状态的字典
    """
    executor = MigrationExecutor()
    history = executor.get_migration_history()
    pending = executor.get_pending_migrations()

    return {
        'total_migrations': len(history),
        'successful': sum(1 for h in history if h['status'] == 'success'),
        'failed': sum(1 for h in history if h['status'] == 'failed'),
        'pending': len(pending),
        'history': history,
        'pending_list': pending
    }
