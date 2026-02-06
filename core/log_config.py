#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一日志配置模块

解决多模块日志配置的代码重复问题
"""

import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from core.config.config import Config


def setup_logger(name: str, level: int = None) -> logging.Logger:
    """统一配置 logger
    
    Args:
        name: logger 名称（通常使用 __name__）
        level: 日志级别，默认从 Config.LOG_LEVEL 获取或使用 DEBUG
        
    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置：如果已经有 handlers，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    if level is None:
        # 尝试从 Config 获取，默认为 DEBUG
        level = getattr(logging, getattr(Config, 'LOG_LEVEL', 'DEBUG'), logging.DEBUG)
    logger.setLevel(level)
    
    # 创建文件 handler
    handler = ConcurrentRotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=Config.MAX_BYTES,
        backupCount=Config.BACKUP_COUNT,
        encoding='utf-8'
    )
    handler.setLevel(level)
    
    # 改进的日志格式：包含文件名和行号
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """获取已配置的 logger（简写）
    
    如果 logger 未配置，会自动调用 setup_logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
