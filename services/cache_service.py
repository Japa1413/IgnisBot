"""
Cache Service - Advanced cache management with TTL and statistics.
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


class CacheService:
    """Advanced cache service with TTL, invalidation, and statistics"""
    
    def __init__(self, ttl_seconds: int = 30):
        """
        Initialize cache service.
        
        Args:
            ttl_seconds: Cache TTL in seconds (default: 30)
        """
        self.ttl = timedelta(seconds=ttl_seconds)
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """
        Get user data from cache.
        
        Args:
            user_id: User ID
        
        Returns:
            User data dict or None if not in cache or expired
        """
        global _cache_hits, _cache_misses
        
        now = datetime.now()
        
        # Check cache
        if user_id in _user_cache:
            data, timestamp = _user_cache[user_id]
            if now - timestamp < self.ttl:
                _cache_hits += 1
                logger.debug(f"Cache hit for user_id {user_id}")
                return data
            else:
                # Cache expired, remove
                del _user_cache[user_id]
        
        # Cache miss
        _cache_misses += 1
        logger.debug(f"Cache miss for user_id {user_id}")
        return None
    
    async def set_user(self, user_id: int, data: dict) -> None:
        """
        Store user data in cache.
        
        Args:
            user_id: User ID
            data: User data dict
        """
        _user_cache[user_id] = (data, datetime.now())
        logger.debug(f"Cache set for user_id {user_id}")
    
    async def invalidate_user(self, user_id: int) -> None:
        """
        Invalidate cache for a specific user.
        
        Args:
            user_id: User ID
        """
        if user_id in _user_cache:
            del _user_cache[user_id]
            logger.debug(f"Cache invalidated for user_id {user_id}")
    
    def clear(self) -> None:
        """Clear all cache"""
        global _user_cache
        _user_cache.clear()
        logger.info("Cache cleared completely")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache statistics
        """
        total = _cache_hits + _cache_misses
        hit_rate = (_cache_hits / total * 100) if total > 0 else 0
        return {
            "hits": _cache_hits,
            "misses": _cache_misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "entries": len(_user_cache),
            "ttl_seconds": int(self.ttl.total_seconds())
        }

