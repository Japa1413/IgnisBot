"""
Unit tests for CacheService

Tests cache functionality and statistics.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from services.cache_service import CacheService


@pytest.mark.asyncio
async def test_get_user_cache_hit():
    """Test get_user returns cached data when not expired"""
    cache = CacheService(ttl_seconds=30)
    
    # Manually add to cache
    from services.cache_service import _user_cache
    _user_cache.clear()
    _user_cache[123] = ({"user_id": 123, "points": 100}, datetime.now())
    
    result = await cache.get_user(123)
    
    assert result == {"user_id": 123, "points": 100}


@pytest.mark.asyncio
async def test_get_user_cache_miss():
    """Test get_user returns None when cache miss"""
    cache = CacheService(ttl_seconds=30)
    
    from services.cache_service import _user_cache
    _user_cache.clear()
    
    result = await cache.get_user(999)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_user_cache_expired():
    """Test get_user returns None when cache expired"""
    cache = CacheService(ttl_seconds=30)
    
    from services.cache_service import _user_cache
    _user_cache.clear()
    # Add expired entry (31 seconds ago)
    expired_time = datetime.now() - timedelta(seconds=31)
    _user_cache[123] = ({"user_id": 123, "points": 100}, expired_time)
    
    result = await cache.get_user(123)
    
    assert result is None
    assert 123 not in _user_cache  # Should be removed


@pytest.mark.asyncio
async def test_set_user():
    """Test set_user stores data in cache"""
    cache = CacheService(ttl_seconds=30)
    
    from services.cache_service import _user_cache
    _user_cache.clear()
    
    await cache.set_user(123, {"user_id": 123, "points": 100})
    
    assert 123 in _user_cache
    data, timestamp = _user_cache[123]
    assert data == {"user_id": 123, "points": 100}


@pytest.mark.asyncio
async def test_invalidate_user():
    """Test invalidate_user removes entry from cache"""
    cache = CacheService(ttl_seconds=30)
    
    from services.cache_service import _user_cache
    _user_cache.clear()
    _user_cache[123] = ({"user_id": 123}, datetime.now())
    
    await cache.invalidate_user(123)
    
    assert 123 not in _user_cache


def test_get_stats():
    """Test get_stats returns cache statistics"""
    cache = CacheService(ttl_seconds=30)
    
    # Clear global stats
    from services.cache_service import _cache_hits, _cache_misses
    global _cache_hits, _cache_misses
    _cache_hits = 80
    _cache_misses = 20
    
    stats = cache.get_stats()
    
    assert stats["hits"] == 80
    assert stats["misses"] == 20
    assert stats["hit_rate"] == "80.0%"
    assert stats["ttl_seconds"] == 30

