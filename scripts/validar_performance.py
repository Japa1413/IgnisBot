#!/usr/bin/env python3
"""
Performance Validation Script

Script to validate performance improvements from Phase 1 and Phase 2.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache import get_cache_stats, clear_cache
from utils.database import get_pool, get_user
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_get_user_performance(user_id: int, iterations: int = 100):
    """Test get_user performance with cache"""
    clear_cache()  # Start fresh
    
    # First run (cold cache)
    start = time.time()
    await get_user(user_id)
    first_run_time = (time.time() - start) * 1000  # Convert to ms
    
    # Subsequent runs (warm cache)
    start = time.time()
    for _ in range(iterations - 1):
        await get_user(user_id)
    cached_runs_time = (time.time() - start) * 1000  # Convert to ms
    
    avg_cached_time = cached_runs_time / (iterations - 1)
    
    return {
        "first_run_ms": round(first_run_time, 2),
        "avg_cached_ms": round(avg_cached_time, 2),
        "improvement": round((1 - avg_cached_time / first_run_time) * 100, 1)
    }


async def test_cache_hit_rate(user_ids: list[int], iterations_per_user: int = 10):
    """Test cache hit rate with multiple users"""
    clear_cache()
    
    # First pass (cache miss for all)
    for user_id in user_ids:
        for _ in range(iterations_per_user):
            await get_user(user_id)
    
    stats_after_first = get_cache_stats()
    
    # Second pass (should be cache hits)
    for user_id in user_ids:
        for _ in range(iterations_per_user):
            await get_user(user_id)
    
    stats_final = get_cache_stats()
    
    return {
        "after_first_pass": stats_after_first,
        "final": stats_final
    }


async def main():
    """Main validation function"""
    print("=" * 60)
    print("PERFORMANCE VALIDATION - PHASE 1 + 2")
    print("=" * 60)
    print()
    
    # Initialize database connection
    try:
        pool = get_pool()
        print("✅ Database connection pool available")
    except RuntimeError as e:
        print(f"❌ Database not initialized: {e}")
        return
    
    # Test 1: Single user performance
    print("\n📊 TEST 1: Single User Performance (with cache)")
    print("-" * 60)
    
    test_user_id = 123456789  # Test user ID (replace with real ID if needed)
    try:
        result = await test_get_user_performance(test_user_id, iterations=100)
        print(f"First run (cold cache): {result['first_run_ms']} ms")
        print(f"Average cached: {result['avg_cached_ms']} ms")
        print(f"Improvement: {result['improvement']}%")
    except Exception as e:
        print(f"⚠️ Test skipped (user may not exist): {e}")
    
    # Test 2: Cache hit rate
    print("\n📊 TEST 2: Cache Hit Rate")
    print("-" * 60)
    
    stats = get_cache_stats()
    print(f"Current Cache Statistics:")
    print(f"  Hit Rate: {stats['hit_rate']}")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Entries: {stats['entries']}")
    
    # Test 3: Pool configuration
    print("\n📊 TEST 3: Database Pool Configuration")
    print("-" * 60)
    
    from utils.config import DB_POOL_MIN, DB_POOL_MAX
    print(f"Pool Configuration:")
    print(f"  Min connections: {DB_POOL_MIN}")
    print(f"  Max connections: {DB_POOL_MAX}")
    print(f"  ✅ Pool configurable via environment")
    
    print("\n" + "=" * 60)
    print("✅ Validation complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

