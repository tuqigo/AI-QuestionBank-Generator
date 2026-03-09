"""日志配置模块"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 创建 logs 目录
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """创建并配置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件 handler (轮转，最大 10MB，保留 5 个文件)
    file_handler = RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 创建各模块日志器
auth_logger = setup_logger("auth")
qwen_logger = setup_logger("qwen")
user_logger = setup_logger("user")
api_logger = setup_logger("api")
