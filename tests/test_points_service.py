"""
Unit tests for PointsService

Tests the service layer with mocked repositories.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.points_service import PointsService, PointsTransaction


@pytest.fixture
def mock_bot():
    """Mock Discord bot"""
    bot = MagicMock()
    bot.dispatch = AsyncMock()
    return bot


@pytest.fixture
def points_service(mock_bot):
    """PointsService instance with mocked dependencies"""
    # Use dependency injection for better testability
    from domain.protocols import UserRepositoryProtocol, ConsentServiceProtocol
    
    mock_user_repo = MagicMock(spec=UserRepositoryProtocol)
    mock_user_repo.get_or_create = AsyncMock(return_value={"user_id": 123, "points": 100})
    mock_user_repo.update_points = AsyncMock(return_value=150)
    
    mock_consent_service = MagicMock(spec=ConsentServiceProtocol)
    mock_consent_service.has_consent = AsyncMock(return_value=True)
    
    service = PointsService(
        mock_bot,
        user_repo=mock_user_repo,
        consent_service=mock_consent_service
    )
    
    return service


@pytest.mark.asyncio
async def test_add_points(points_service, mock_bot):
    """Test add_points creates transaction and dispatches event"""
    transaction = await points_service.add_points(
        user_id=123,
        amount=50,
        reason="Test",
        performed_by=456
    )
    
    assert isinstance(transaction, PointsTransaction)
    assert transaction.user_id == 123
    assert transaction.before == 100
    assert transaction.after == 150
    assert transaction.delta == 50
    assert transaction.reason == "Test"
    assert transaction.performed_by == 456
    
    # Verify repository was called
    points_service.user_repo.get_or_create.assert_called_once_with(123)
    points_service.user_repo.update_points.assert_called_once_with(123, 50)


@pytest.mark.asyncio
async def test_remove_points(points_service, mock_bot):
    """Test remove_points removes points correctly"""
    transaction = await points_service.remove_points(
        user_id=123,
        amount=30,
        reason="Test removal",
        performed_by=456
    )
    
    assert isinstance(transaction, PointsTransaction)
    assert transaction.user_id == 123
    assert transaction.before == 100
    assert transaction.after == 150  # Mock returns this
    assert transaction.delta == -30  # Negative delta
    assert transaction.reason == "Test removal"
    
    # Verify repository was called with negative value
    points_service.user_repo.get.assert_called_once_with(123)
    points_service.user_repo.update_points.assert_called_once_with(123, -30)


@pytest.mark.asyncio
async def test_remove_points_user_not_found(points_service, mock_bot):
    """Test remove_points raises ValueError if user not found"""
    points_service.user_repo.get = AsyncMock(return_value=None)
    
    with pytest.raises(ValueError, match="not found"):
        await points_service.remove_points(
            user_id=999,
            amount=10,
            reason="Test",
            performed_by=456
        )


@pytest.mark.asyncio
async def test_add_points_without_consent(mock_bot):
    """Test add_points raises ValueError when user hasn't given consent"""
    from domain.protocols import UserRepositoryProtocol, ConsentServiceProtocol
    
    mock_user_repo = MagicMock(spec=UserRepositoryProtocol)
    mock_user_repo.get_or_create = AsyncMock(return_value={"user_id": 123, "points": 100})
    
    mock_consent_service = MagicMock(spec=ConsentServiceProtocol)
    mock_consent_service.has_consent = AsyncMock(return_value=False)  # No consent
    
    service = PointsService(
        mock_bot,
        user_repo=mock_user_repo,
        consent_service=mock_consent_service
    )
    
    with pytest.raises(ValueError, match="consent"):
        await service.add_points(
            user_id=123,
            amount=50,
            reason="Test",
            performed_by=456,
            check_consent=True
        )
    
    # Verify consent was checked
    mock_consent_service.has_consent.assert_called_once_with(123)
    # Verify points were NOT updated
    mock_user_repo.update_points.assert_not_called()


@pytest.mark.asyncio
async def test_remove_points_without_consent(mock_bot):
    """Test remove_points raises ValueError when user hasn't given consent"""
    from domain.protocols import UserRepositoryProtocol, ConsentServiceProtocol
    
    mock_user_repo = MagicMock(spec=UserRepositoryProtocol)
    mock_user_repo.get = AsyncMock(return_value={"user_id": 123, "points": 100})
    
    mock_consent_service = MagicMock(spec=ConsentServiceProtocol)
    mock_consent_service.has_consent = AsyncMock(return_value=False)  # No consent
    
    service = PointsService(
        mock_bot,
        user_repo=mock_user_repo,
        consent_service=mock_consent_service
    )
    
    with pytest.raises(ValueError, match="consent"):
        await service.remove_points(
            user_id=123,
            amount=50,
            reason="Test",
            performed_by=456,
            check_consent=True
        )
    
    # Verify consent was checked
    mock_consent_service.has_consent.assert_called_once_with(123)
    # Verify points were NOT updated
    mock_user_repo.update_points.assert_not_called()


@pytest.mark.asyncio
async def test_add_points_check_consent_false(mock_bot):
    """Test add_points bypasses consent when check_consent=False"""
    from domain.protocols import UserRepositoryProtocol, ConsentServiceProtocol
    
    mock_user_repo = MagicMock(spec=UserRepositoryProtocol)
    mock_user_repo.get_or_create = AsyncMock(return_value={"user_id": 123, "points": 100})
    mock_user_repo.update_points = AsyncMock(return_value=150)
    
    mock_consent_service = MagicMock(spec=ConsentServiceProtocol)
    mock_consent_service.has_consent = AsyncMock(return_value=False)  # No consent
    
    service = PointsService(
        mock_bot,
        user_repo=mock_user_repo,
        consent_service=mock_consent_service
    )
    
    # Should work even without consent when check_consent=False
    transaction = await service.add_points(
        user_id=123,
        amount=50,
        reason="Test",
        performed_by=456,
        check_consent=False  # Bypass consent
    )
    
    assert transaction.after == 150
    # Consent should NOT be checked
    mock_consent_service.has_consent.assert_not_called()
    # Points should be updated
    mock_user_repo.update_points.assert_called_once_with(123, 50)


@pytest.mark.asyncio
async def test_remove_points_check_consent_false(mock_bot):
    """Test remove_points bypasses consent when check_consent=False"""
    from domain.protocols import UserRepositoryProtocol, ConsentServiceProtocol
    
    mock_user_repo = MagicMock(spec=UserRepositoryProtocol)
    mock_user_repo.get = AsyncMock(return_value={"user_id": 123, "points": 100})
    mock_user_repo.update_points = AsyncMock(return_value=50)
    
    mock_consent_service = MagicMock(spec=ConsentServiceProtocol)
    mock_consent_service.has_consent = AsyncMock(return_value=False)  # No consent
    
    service = PointsService(
        mock_bot,
        user_repo=mock_user_repo,
        consent_service=mock_consent_service
    )
    
    # Should work even without consent when check_consent=False
    transaction = await service.remove_points(
        user_id=123,
        amount=50,
        reason="Test",
        performed_by=456,
        check_consent=False  # Bypass consent
    )
    
    assert transaction.after == 50
    assert transaction.delta == -50
    # Consent should NOT be checked
    mock_consent_service.has_consent.assert_not_called()
    # Points should be updated
    mock_user_repo.update_points.assert_called_once_with(123, -50)


@pytest.mark.asyncio
async def test_add_points_creates_complete_transaction(points_service, mock_bot):
    """Test add_points returns complete PointsTransaction with all fields"""
    transaction = await points_service.add_points(
        user_id=123,
        amount=50,
        reason="Complete test",
        performed_by=789
    )
    
    # Verify all transaction fields
    assert transaction.user_id == 123
    assert transaction.before == 100
    assert transaction.after == 150
    assert transaction.delta == 50
    assert transaction.reason == "Complete test"
    assert transaction.performed_by == 789
    assert transaction.timestamp is not None

