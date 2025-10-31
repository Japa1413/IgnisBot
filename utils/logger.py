# utils/logger.py
"""
Sistema de Logging Estruturado para IgnisBot

Implementa logging estruturado com rotação de arquivos e níveis configuráveis.
Suporta auditoria LGPD e logging de segurança.
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
    """Formatador JSON para logs estruturados (facilita parsing e análise)"""
    
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
        
        # Adicionar contexto adicional se disponível
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "extra_data"):
            log_data["extra_data"] = record.extra_data
            
        # Adicionar exception se houver
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
    Configura e retorna um logger estruturado.
    
    Args:
        name: Nome do logger
        log_file: Caminho do arquivo de log (None = apenas console)
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Tamanho máximo do arquivo antes de rotação
        backup_count: Número de arquivos de backup a manter
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Formato para console (legível)
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Formato JSON para arquivo (estruturado)
    file_format = StructuredFormatter()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Arquivo recebe todos os níveis
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# Logger global configurado
_LOGGER: Optional[logging.Logger] = None

def get_logger(name: str = "ignisbot") -> logging.Logger:
    """
    Obtém o logger global configurado.
    
    Args:
        name: Nome do logger (padrão: "ignisbot")
    
    Returns:
        Logger configurado
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
    Registra acesso a dados pessoais (LGPD Art. 10).
    
    Args:
        user_id: ID do usuário cujos dados foram acessados
        action_type: Tipo de ação (CREATE, READ, UPDATE, DELETE, EXPORT, etc.)
        data_type: Tipo de dado acessado (user_data, points, rank, etc.)
        performed_by: ID do usuário que realizou a ação (None = próprio usuário)
        purpose: Finalidade do acesso
        details: Detalhes adicionais da operação
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

