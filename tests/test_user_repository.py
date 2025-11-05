"""
Unit tests for UserRepository

Tests the repository layer in isolation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from repositories.user_repository import UserRepository


@pytest.fixture
def mock_pool():
    """Mock database pool"""
    pool = MagicMock()
    conn = AsyncMock()
    cursor = AsyncMock()
    
    async def acquire():
        return conn
    
    pool.acquire = AsyncMock(return_value=conn)
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)
    conn.cursor = AsyncMock(return_value=cursor)
    cursor.__aenter__ = AsyncMock(return_value=cursor)
    cursor.__aexit__ = AsyncMock(return_value=None)
    
    return pool, cursor


@pytest.fixture
def user_repo(mock_pool):
    """UserRepository instance with mocked pool"""
    pool, cursor = mock_pool
    repo = UserRepository()
    repo._pool = pool
    return repo, cursor


@pytest.mark.asyncio
async def test_get_user_cache_hit(user_repo):
    """Test get_user returns cached data when available"""
    repo, cursor = user_repo
    
    # Mock cache hit
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        cache_service.get_user = AsyncMock(return_value={"user_id": 123, "points": 100})
        mock_cache.return_value = cache_service
        
        result = await repo.get(123)
        
        assert result == {"user_id": 123, "points": 100}
        cache_service.get_user.assert_called_once_with(123)
        cursor.execute.assert_not_called()  # Should not query DB


@pytest.mark.asyncio
async def test_get_user_cache_miss(user_repo):
    """Test get_user queries database on cache miss"""
    repo, cursor = user_repo
    
    # Mock cache miss (returns None)
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        cache_service.get_user = AsyncMock(return_value=None)
        cache_service.set_user = AsyncMock()
        mock_cache.return_value = cache_service
        
        # Mock database query result
        cursor.execute = AsyncMock()
        cursor.fetchone = AsyncMock(return_value={"user_id": 123, "points": 100})
        
        result = await repo.get(123)
        
        assert result == {"user_id": 123, "points": 100}
        cache_service.get_user.assert_called_once_with(123)
        cursor.execute.assert_called()  # Should query DB
        cache_service.set_user.assert_called_once_with(123, {"user_id": 123, "points": 100})


@pytest.mark.asyncio
async def test_create_user(user_repo):
    """Test create_user inserts new user and invalidates cache"""
    repo, cursor = user_repo
    
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        cache_service.invalidate_user = AsyncMock()
        mock_cache.return_value = cache_service
        
        cursor.execute = AsyncMock()
        cursor.rowcount = 1
        
        await repo.create(123)
        
        cursor.execute.assert_called()
        cache_service.invalidate_user.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_update_points(user_repo):
    """Test update_points updates user points and returns new value"""
    repo, cursor = user_repo
    
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        cache_service.invalidate_user = AsyncMock()
        mock_cache.return_value = cache_service
        
        # Mock UPDATE query
        cursor.execute = AsyncMock()
        # Mock SELECT query for new value
        cursor.fetchone = AsyncMock(return_value=(150,))
        
        new_points = await repo.update_points(123, 50)
        
        assert new_points == 150
        assert cursor.execute.call_count == 2  # UPDATE + SELECT
        cache_service.invalidate_user.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_get_user_without_cache(user_repo):
    """Test get_user bypasses cache when use_cache=False"""
    repo, cursor = user_repo
    
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        mock_cache.return_value = cache_service
        
        cursor.execute = AsyncMock()
        cursor.fetchone = AsyncMock(return_value={"user_id": 123, "points": 100})
        
        result = await repo.get(123, use_cache=False)
        
        assert result == {"user_id": 123, "points": 100}
        # Cache should not be checked
        cache_service.get_user.assert_not_called()
        cursor.execute.assert_called()


@pytest.mark.asyncio
async def test_get_or_create_existing(user_repo):
    """Test get_or_create returns existing user"""
    repo, cursor = user_repo
    
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        mock_cache.return_value = cache_service
        
        # Mock existing user
        cursor.execute = AsyncMock()
        cursor.fetchone = AsyncMock(return_value={"user_id": 123, "points": 100})
        
        result = await repo.get_or_create(123)
        
        assert result["user_id"] == 123
        # Should not create new user
        assert cursor.execute.call_count == 1  # Only SELECT


@pytest.mark.asyncio
async def test_get_or_create_new(user_repo):
    """Test get_or_create creates new user when not exists"""
    repo, cursor = user_repo
    
    with patch.object(repo, '_get_cache') as mock_cache:
        cache_service = MagicMock()
        cache_service.invalidate_user = AsyncMock()
        mock_cache.return_value = cache_service
        
        # First call returns None (not found)
        # Second call returns new user
        cursor.execute = AsyncMock()
        cursor.fetchone = AsyncMock(side_effect=[None, {"user_id": 123, "points": 0}])
        cursor.rowcount = 1
        
        result = await repo.get_or_create(123)
        
        assert result["user_id"] == 123
        # Should have called INSERT
        assert cursor.execute.call_count >= 2
        cache_service.invalidate_user.assert_called()


@pytest.mark.asyncio
async def test_exists_true(user_repo):
    """Test exists returns True when user exists"""
    repo, cursor = user_repo
    
    cursor.execute = AsyncMock()
    cursor.fetchone = AsyncMock(return_value=(1,))
    
    result = await repo.exists(123)
    
    assert result is True


@pytest.mark.asyncio
async def test_exists_false(user_repo):
    """Test exists returns False when user doesn't exist"""
    repo, cursor = user_repo
    
    cursor.execute = AsyncMock()
    cursor.fetchone = AsyncMock(return_value=None)
    
    result = await repo.exists(999)
    
    assert result is False

