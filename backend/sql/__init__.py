"""数据库初始化 - 执行 schema.sql 创建所有表"""

import sqlite3
from pathlib import Path

# SQL 文件路径
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
# 数据库文件路径
DB_PATH = Path(__file__).parent.parent / "data" / "users.db"


def init_database():
    """初始化数据库，执行 schema.sql 中的所有 DDL 语句"""
    # 确保数据库目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(str(DB_PATH))

    try:
        # 读取 schema.sql 文件
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 执行所有 SQL 语句
        conn.executescript(schema_sql)
        conn.commit()

        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败：{e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
