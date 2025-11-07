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

# In-memory cache: {user_id: (data, timestamp)}
_user_cache: Dict[int, Tuple[dict, datetime]] = {}

# Default TTL: 30 seconds
CACHE_TTL = timedelta(seconds=30)

# Statistics
_cache_hits = 0
_cache_misses = 0
_cache_evictions = 0
_cache_warming_enabled = False
_active_users: set[int] = set()  # Track active users for cache warming


def get_cache_stats() -> dict:
    """Returns cache statistics"""
    total = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total * 100) if total > 0 else 0
    eviction_rate = (_cache_evictions / total * 100) if total > 0 else 0
    return {
        "hits": _cache_hits,
        "misses": _cache_misses,
        "evictions": _cache_evictions,
        "hit_rate": f"{hit_rate:.1f}%",
        "eviction_rate": f"{eviction_rate:.1f}%",
        "entries": len(_user_cache),
        "active_users": len(_active_users),
        "warming_enabled": _cache_warming_enabled
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
            global _cache_evictions
            _cache_evictions += 1
    
    # Cache miss - fetch from database
    _cache_misses += 1
    logger.debug(f"Cache miss for user_id {user_id}")
    
    # CRITICAL FIX: Call repository directly to avoid recursion
    # get_user() would call get_user_cached() again, causing infinite recursion
    try:
        from repositories.user_repository import UserRepository
        repo = UserRepository()
        # Use use_cache=False to break recursion cycle
        data = await repo.get(user_id, use_cache=False)
    except ImportError:
        # Fallback: direct database query if repository not available
        from utils.database import _POOL
        import aiomysql
        
        if _POOL is None:
            logger.error("Database pool not initialized")
            return None
        
        async with _POOL.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT user_id, points, exp, `rank`, path, next_rank, last_update, company, speciality, service_studs FROM users WHERE user_id = %s",
                    (user_id,)
                )
                data = await cursor.fetchone()
    
    # Store in cache (even if None, to avoid repeated queries)
    if data is not None:
        _user_cache[user_id] = (data, now)
        # Track active user for cache warming
        _active_users.add(user_id)
    
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


async def warm_cache_for_users(user_ids: list[int]):
    """
    Warm cache for a list of user IDs.
    Useful for pre-loading data for active users.
    
    Args:
        user_ids: List of user IDs to warm cache for
    """
    global _cache_warming_enabled
    if not _cache_warming_enabled:
        return
    
    logger.info(f"Warming cache for {len(user_ids)} users")
    for user_id in user_ids:
        try:
            await get_user_cached(user_id)
        except Exception as e:
            logger.warning(f"Failed to warm cache for user {user_id}: {e}")


def enable_cache_warming():
    """Enable cache warming for active users"""
    global _cache_warming_enabled
    _cache_warming_enabled = True
    logger.info("Cache warming enabled")


def disable_cache_warming():
    """Disable cache warming"""
    global _cache_warming_enabled
    _cache_warming_enabled = False
    logger.info("Cache warming disabled")


def add_active_user(user_id: int):
    """Add user to active users list for cache warming"""
    _active_users.add(user_id)


def remove_active_user(user_id: int):
    """Remove user from active users list"""
    _active_users.discard(user_id)


def get_active_users() -> list[int]:
    """Get list of active user IDs"""
    return list(_active_users)

