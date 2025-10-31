# utils/cache.py
"""
Sistema de Cache para Dados de Usuário

Implementa cache com TTL (Time To Live) para reduzir queries ao banco de dados.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Cache em memória: {user_id: (data, timestamp)}
_user_cache: Dict[int, Tuple[dict, datetime]] = {}

# TTL padrão: 30 segundos
CACHE_TTL = timedelta(seconds=30)

# Estatísticas
_cache_hits = 0
_cache_misses = 0


def get_cache_stats() -> dict:
    """Retorna estatísticas do cache"""
    total = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total * 100) if total > 0 else 0
    return {
        "hits": _cache_hits,
        "misses": _cache_misses,
        "hit_rate": f"{hit_rate:.1f}%",
        "entries": len(_user_cache)
    }


async def get_user_cached(user_id: int) -> Optional[dict]:
    """
    Obtém dados do usuário com cache TTL.
    
    Args:
        user_id: ID do usuário
    
    Returns:
        Dict com dados do usuário ou None se não encontrado
    
    Raises:
        RuntimeError: Se o pool de banco não estiver inicializado
    """
    global _cache_hits, _cache_misses
    now = datetime.now()
    
    # Verificar cache
    if user_id in _user_cache:
        data, timestamp = _user_cache[user_id]
        if now - timestamp < CACHE_TTL:
            _cache_hits += 1
            logger.debug(f"Cache hit para user_id {user_id}")
            return data
        else:
            # Cache expirado, remover
            del _user_cache[user_id]
    
    # Cache miss - buscar do banco
    _cache_misses += 1
    logger.debug(f"Cache miss para user_id {user_id}")
    
    from utils.database import get_user
    data = await get_user(user_id)
    
    # Armazenar no cache (mesmo que None, para evitar queries repetidas)
    if data is not None:
        _user_cache[user_id] = (data, now)
    
    return data


def invalidate_user_cache(user_id: int):
    """
    Invalida o cache de um usuário específico.
    
    Use quando os dados do usuário foram modificados.
    
    Args:
        user_id: ID do usuário
    """
    if user_id in _user_cache:
        del _user_cache[user_id]
        logger.debug(f"Cache invalidado para user_id {user_id}")


def clear_cache():
    """Limpa todo o cache"""
    global _user_cache
    _user_cache.clear()
    logger.info("Cache limpo completamente")


def set_cache_ttl(seconds: int):
    """
    Define o TTL do cache em segundos.
    
    Args:
        seconds: TTL em segundos
    """
    global CACHE_TTL
    CACHE_TTL = timedelta(seconds=seconds)
    logger.info(f"Cache TTL atualizado para {seconds} segundos")

