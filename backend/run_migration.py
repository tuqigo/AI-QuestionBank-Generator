"""
运行数据库迁移 002
"""
import sqlite3
import os

# 使用绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "tixiaobao.db")
MIGRATION_PATH = os.path.join(BASE_DIR, "db", "migrations", "002_add_question_templates.sql")

def run_migration():
    """执行迁移 SQL 文件"""
    if not os.path.exists(MIGRATION_PATH):
        print(f"迁移文件不存在：{MIGRATION_PATH}")
        return False

    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在：{DB_PATH}")
        return False

    with open(MIGRATION_PATH, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        # 执行多条 SQL 语句
        conn.executescript(sql_script)
        conn.commit()
        print("数据库迁移 002 执行成功！")
        return True
    except Exception as e:
        print(f"数据库迁移失败：{e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
