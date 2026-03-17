"""
数据库迁移管理 CLI

使用方法：
    python -m db.migrations_cli status    # 查看迁移状态
    python -m db.migrations_cli migrate   # 执行迁移
    python -m db.migrations_cli pending   # 查看待执行迁移
    python -m db.migrations_cli history   # 查看迁移历史
"""

import sys
import json
from datetime import datetime

from db.migrations import MigrationExecutor, get_migration_status


def cmd_status():
    """查看迁移状态摘要"""
    status = get_migration_status()
    print("=" * 60)
    print("数据库迁移状态")
    print("=" * 60)
    print(f"总迁移数：{status['total_migrations']}")
    print(f"成功：{status['successful']}")
    print(f"失败：{status['failed']}")
    print(f"待执行：{status['pending']}")
    print("=" * 60)


def cmd_migrate():
    """执行数据库迁移"""
    print("开始执行数据库迁移...")
    executor = MigrationExecutor()
    try:
        executed = executor.migrate()
        if executed:
            print(f"\n成功执行 {len(executed)} 个迁移:")
            for name in executed:
                print(f"  - {name}")
        else:
            print("数据库已是最新版本，无需迁移")
    except Exception as e:
        print(f"迁移失败：{e}")
        sys.exit(1)


def cmd_pending():
    """查看待执行的迁移"""
    executor = MigrationExecutor()
    pending = executor.get_pending_migrations()
    if pending:
        print("待执行的迁移:")
        for name in pending:
            print(f"  - {name}")
    else:
        print("没有待执行的迁移")


def cmd_history():
    """查看迁移历史记录"""
    executor = MigrationExecutor()
    history = executor.get_migration_history()
    if not history:
        print("暂无迁移记录")
        return

    print("=" * 80)
    print(f"{'版本':<8} {'状态':<10} {'文件名':<45} {'执行时间'}")
    print("=" * 80)
    for record in history:
        version = record['version']
        status = record['status']
        filename = record['filename']
        executed_at = record['executed_at']
        print(f"{version:<8} {status:<10} {filename:<45} {executed_at}")
    print("=" * 80)
    print(f"共 {len(history)} 条记录")


def cmd_json():
    """以 JSON 格式输出迁移状态（用于程序调用）"""
    status = get_migration_status()
    print(json.dumps(status, indent=2, default=str))


def print_usage():
    """打印使用说明"""
    print("""
数据库迁移管理工具

使用方法:
    python -m db.migrations_cli <command>

可用命令:
    status    - 查看迁移状态摘要
    migrate   - 执行数据库迁移
    pending   - 查看待执行的迁移
    history   - 查看迁移历史记录
    json      - 以 JSON 格式输出迁移状态
    help      - 显示此帮助信息

示例:
    python -m db.migrations_cli status
    python -m db.migrations_cli migrate
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    commands = {
        'status': cmd_status,
        'migrate': cmd_migrate,
        'pending': cmd_pending,
        'history': cmd_history,
        'json': cmd_json,
        'help': print_usage,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"未知命令：{command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
