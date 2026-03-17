"""
数据库初始化模块

说明：
- 本模块仅负责执行 schema.sql 创建基础表结构
- 增量迁移请通过 `python -m db.migrations_cli migrate` 手动执行
- 多实例部署时，迁移应在 CI/CD 阶段独立执行，避免并发问题
"""

import sqlite3
from pathlib import Path

# SQL 文件路径
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
# 数据库文件路径 - 使用 config 中的统一配置
from config import DB_PATH


def init_database():
    """
    初始化数据库 - 仅执行 schema.sql 创建基础表

    注意：
    - 不再自动执行增量迁移
    - 增量迁移请通过 `python -m db.migrations_cli migrate` 手动执行
    - 多实例部署时，迁移应在 CI/CD 阶段独立执行
    """
    # 确保数据库目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(str(DB_PATH))

    try:
        # 执行 schema.sql 创建基础表（如果文件存在）
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
            print("基础表结构创建完成")
        else:
            print("schema.sql 不存在，跳过基础表创建")

        print("数据库初始化完成，如需执行增量迁移请运行：python -m db.migrations_cli migrate")
    except Exception as e:
        print(f"数据库初始化失败：{e}")
        raise
    finally:
        conn.close()


def get_migration_status():
    """获取迁移状态信息"""
    from db.migrations import get_migration_status as _get_status
    return _get_status()


if __name__ == "__main__":
    init_database()
