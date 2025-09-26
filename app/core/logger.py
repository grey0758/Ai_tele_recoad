# -*- coding: utf-8 -*-
"""
日志配置模块
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console
from app.core.config import settings

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)


def setup_logging():
    """设置全局日志配置"""
    root_logger = logging.getLogger()
    # 清理已存在的处理器，避免重复添加
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    log_level = getattr(settings, "log_level", "INFO")
    if isinstance(log_level, str):
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    else:
        root_logger.setLevel(logging.INFO)

    # 禁用watchfiles的DEBUG日志，避免日志循环
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    # Rich 控制台处理器
    console_handler = RichHandler(
        console=Console(stderr=True),
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
    )
    console_handler.setLevel(logging.INFO)

    # 轮转文件处理器，避免单文件变大导致频繁变更
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


# 初始化全局日志配置
setup_logging()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取logger实例

    Args:
        name: logger名称，如果为None则返回根logger

    Returns:
        logging.Logger: 配置好的logger实例
    """
    if name is None:
        return logging.getLogger("ai_tele")

    # 获取指定名称的logger
    logger_inside = logging.getLogger(name)

    # 确保logger级别设置正确
    log_level = getattr(settings, "log_level", "INFO")
    logger_inside.setLevel(getattr(logging, str(log_level).upper(), logging.INFO))

    return logger_inside


# 主应用logger（向后兼容）
logger = get_logger("ai_tele")
