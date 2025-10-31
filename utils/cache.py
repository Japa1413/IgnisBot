# utils/cache.py
"""
User Data Cache System

Implements cache with TTL (Time To Live) to reduce database queries.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Cache em memória: {user_id: (data, timestamp)}
_user_cache: Dict[int, Tuple[dict, datetime]] = {}

# Default TTL: 30 seconds
CACHE_TTL = timedelta(seconds=30)

# Statistics
_cache_hits = 0
_cache_misses = 0


def get_cache_stats() -> dict:
    """Returns cache statistics"""
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
    Get user data with TTL cache.
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with user data or None if not found
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    global _cache_hits, _cache_misses
    now = datetime.now()
    
    # Check cache
    if user_id in _user_cache:
        data, timestamp = _user_cache[user_id]
        if now - timestamp < CACHE_TTL:
            _cache_hits += 1
            logger.debug(f"Cache hit for user_id {user_id}")
            return data
        else:
            # Cache expired, remove
            del _user_cache[user_id]
    
    # Cache miss - fetch from database
    _cache_misses += 1
    logger.debug(f"Cache miss for user_id {user_id}")
    
    from utils.database import get_user
    data = await get_user(user_id)
    
    # Store in cache (even if None, to avoid repeated queries)
    if data is not None:
        _user_cache[user_id] = (data, now)
    
    return data


def invalidate_user_cache(user_id: int):
    """
    Invalidates cache for a specific user.
    
    Use when user data has been modified.
    
    Args:
        user_id: User ID
    """
    if user_id in _user_cache:
        del _user_cache[user_id]
        logger.debug(f"Cache invalidated for user_id {user_id}")


def clear_cache():
    """Clears all cache"""
    global _user_cache
    _user_cache.clear()
    logger.info("Cache cleared completely")


def set_cache_ttl(seconds: int):
    """
    Set cache TTL in seconds.
    
    Args:
        seconds: TTL in seconds
    """
    global CACHE_TTL
    CACHE_TTL = timedelta(seconds=seconds)
    logger.info(f"Cache TTL updated to {seconds} seconds")

