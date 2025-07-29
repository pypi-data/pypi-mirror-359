# eops/utils/logger.py
import logging
import sys
from typing import Optional

# 全局的 logger 注册表，防止重复创建
_loggers = {}

class InstanceFilter(logging.Filter):
    """A filter to add the instance_id to log records."""
    def __init__(self, instance_id: str):
        super().__init__()
        self.instance_id = instance_id

    def filter(self, record):
        record.instance_id = self.instance_id
        return True

def setup_logger(instance_id: Optional[str] = "main"):
    """
    Sets up a logger that is unique to a given instance_id.
    This prevents log messages from different strategy instances from mixing up.

    Args:
        instance_id: A unique identifier for the logger instance.
    """
    if instance_id in _loggers:
        return _loggers[instance_id]

    logger = logging.getLogger(f"eops.{instance_id}")
    
    # 防止日志消息传播到根 logger
    logger.propagate = False
    
    # 如果已经有处理器，直接返回，避免重复添加
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    
    # 添加 instance_id 到日志格式中
    formatter = logging.Formatter(
        '%(asctime)s - eops [inst:%(instance_id)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # 添加过滤器
    logger.addFilter(InstanceFilter(instance_id))
    logger.addHandler(handler)
    
    _loggers[instance_id] = logger
    return logger

# 提供一个默认的 logger，用于框架自身的非实例相关日志
log = setup_logger("framework")