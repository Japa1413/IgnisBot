"""
Tests for UserService.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from domain.protocols import UserRepositoryProtocol, CacheServiceProtocol
from services.user_service import UserService


@pytest.fixture
def mock_user_repo():
    """Mock user repository"""
    return MagicMock(spec=UserRepositoryProtocol)


@pytest.fixture
def mock_cache_service():
    """Mock cache service"""
    return MagicMock(spec=CacheServiceProtocol)


@pytest.fixture
def user_service(mock_user_repo, mock_cache_service):
    """UserService instance with mocked dependencies"""
    return UserService(user_repo=mock_user_repo, cache_service=mock_cache_service)


@pytest.mark.asyncio
async def test_get_user_cache_hit(user_service, mock_user_repo, mock_cache_service):
    """Test get_user uses cache when available"""
    cached_data = {"user_id": 123, "points": 100}
    mock_cache_service.get_user = AsyncMock(return_value=cached_data)
    
    result = await user_service.get_user(123, use_cache=True)
    
    assert result == cached_data
    mock_cache_service.get_user.assert_called_once_with(123)
    # Should not call repository when cache hit
    mock_user_repo.get.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_cache_miss(user_service, mock_user_repo, mock_cache_service):
    """Test get_user falls back to repository when cache miss"""
    db_data = {"user_id": 123, "points": 100}
    mock_cache_service.get_user = AsyncMock(return_value=None)  # Cache miss
    mock_user_repo.get = AsyncMock(return_value=db_data)
    
    result = await user_service.get_user(123, use_cache=True)
    
    assert result == db_data
    mock_cache_service.get_user.assert_called_once_with(123)
    mock_user_repo.get.assert_called_once_with(123, use_cache=True)


@pytest.mark.asyncio
async def test_get_user_without_cache(user_service, mock_user_repo, mock_cache_service):
    """Test get_user bypasses cache when use_cache=False"""
    db_data = {"user_id": 123, "points": 100}
    mock_user_repo.get = AsyncMock(return_value=db_data)
    
    result = await user_service.get_user(123, use_cache=False)
    
    assert result == db_data
    # Cache should not be called
    mock_cache_service.get_user.assert_not_called()
    mock_user_repo.get.assert_called_once_with(123, use_cache=False)


@pytest.mark.asyncio
async def test_get_user_not_found(user_service, mock_user_repo, mock_cache_service):
    """Test get_user returns None when user not found"""
    mock_cache_service.get_user = AsyncMock(return_value=None)
    mock_user_repo.get = AsyncMock(return_value=None)
    
    result = await user_service.get_user(999, use_cache=True)
    
    assert result is None


@pytest.mark.asyncio
async def test_ensure_exists_new_user(user_service, mock_user_repo):
    """Test ensure_exists creates new user when not exists"""
    new_user = {"user_id": 123, "points": 0}
    mock_user_repo.get_or_create = AsyncMock(return_value=new_user)
    
    result = await user_service.ensure_exists(123)
    
    assert result == new_user
    mock_user_repo.get_or_create.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_ensure_exists_existing_user(user_service, mock_user_repo):
    """Test ensure_exists returns existing user"""
    existing_user = {"user_id": 123, "points": 100}
    mock_user_repo.get_or_create = AsyncMock(return_value=existing_user)
    
    result = await user_service.ensure_exists(123)
    
    assert result == existing_user
    mock_user_repo.get_or_create.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_user_service_without_injection():
    """Test UserService works without dependency injection (backward compatibility)"""
    service = UserService()
    
    # Should not raise error
    assert service.user_repo is not None
    assert service.cache_service is not None

