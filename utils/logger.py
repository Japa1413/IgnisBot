# utils/logger.py
"""
Structured Logging System for IgnisBot

Implements structured logging with file rotation and configurable levels.
Supports LGPD audit and security logging.
"""

from __future__ import annotations

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from utils.config import LOG_LEVEL, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs (facilitates parsing and analysis)"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add additional context if available
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "extra_data"):
            log_data["extra_data"] = record.extra_data
            
        # Add exception if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(
    name: str = "ignisbot",
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure and return a structured logger.
    
    Args:
        name: Logger name
        log_file: Log file path (None = console only)
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum file size before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid handler duplication
    if logger.handlers:
        return logger
    
    # Format for console (readable)
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # JSON format for file (structured)
    file_format = StructuredFormatter()
    
    # Handler for console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Handler for file (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File receives all levels
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# Global configured logger
_LOGGER: Optional[logging.Logger] = None

def get_logger(name: str = "ignisbot") -> logging.Logger:
    """
    Get the global configured logger.
    
    Args:
        name: Logger name (default: "ignisbot")
    
    Returns:
        Configured logger
    """
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = setup_logger(
            name=name,
            log_file=LOG_FILE,
            log_level=LOG_LEVEL,
            max_bytes=LOG_MAX_SIZE,
            backup_count=LOG_BACKUP_COUNT
        )
    return _LOGGER


def log_data_access(
    user_id: int,
    action_type: str,
    data_type: str,
    performed_by: Optional[int] = None,
    purpose: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Logs personal data access (LGPD Art. 10).
    
    Args:
        user_id: ID of user whose data was accessed
        action_type: Action type (CREATE, READ, UPDATE, DELETE, EXPORT, etc.)
        data_type: Type of data accessed (user_data, points, rank, etc.)
        performed_by: ID of user who performed the action (None = user themselves)
        purpose: Purpose of access
        details: Additional operation details
    """
    logger = get_logger("ignisbot.audit")
    
    log_record = logger.makeRecord(
        logger.name,
        logging.INFO,
        __file__,
        0,
        f"Data access: {action_type} on {data_type} for user {user_id}",
        (),
        None
    )
    log_record.user_id = user_id
    log_record.action = action_type
    log_record.extra_data = {
        "data_type": data_type,
        "performed_by": performed_by,
        "purpose": purpose,
        "details": details or {}
    }
    
    logger.handle(log_record)

