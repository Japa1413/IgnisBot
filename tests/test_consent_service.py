"""
Tests for ConsentService.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from domain.protocols import ConsentRepositoryProtocol
from services.consent_service import ConsentService


@pytest.fixture
def mock_consent_repo():
    """Mock consent repository"""
    return MagicMock(spec=ConsentRepositoryProtocol)


@pytest.fixture
def consent_service(mock_consent_repo):
    """ConsentService instance with mocked dependencies"""
    return ConsentService(consent_repo=mock_consent_repo)


@pytest.mark.asyncio
async def test_has_consent_true(consent_service, mock_consent_repo):
    """Test has_consent returns True when user has given consent"""
    mock_consent_repo.has_consent = AsyncMock(return_value=True)
    
    result = await consent_service.has_consent(123)
    
    assert result is True
    mock_consent_repo.has_consent.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_has_consent_false(consent_service, mock_consent_repo):
    """Test has_consent returns False when user hasn't given consent"""
    mock_consent_repo.has_consent = AsyncMock(return_value=False)
    
    result = await consent_service.has_consent(123)
    
    assert result is False
    mock_consent_repo.has_consent.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_has_consent_none(consent_service, mock_consent_repo):
    """Test has_consent returns False when user consent is None"""
    mock_consent_repo.has_consent = AsyncMock(return_value=False)
    
    result = await consent_service.has_consent(999)
    
    assert result is False


@pytest.mark.asyncio
async def test_grant_consent(consent_service, mock_consent_repo):
    """Test grant_consent calls repository with correct parameters"""
    mock_consent_repo.give_consent = AsyncMock()
    
    await consent_service.give_consent(
        user_id=123,
        base_legal="consentimento",
        version="1.0"
    )
    
    mock_consent_repo.give_consent.assert_called_once_with(
        123,
        "consentimento",
        "1.0"
    )


@pytest.mark.asyncio
async def test_grant_consent_defaults(consent_service, mock_consent_repo):
    """Test grant_consent uses default parameters"""
    from utils.consent_manager import DEFAULT_BASE_LEGAL, CURRENT_CONSENT_VERSION
    mock_consent_repo.give_consent = AsyncMock()
    
    await consent_service.give_consent(user_id=123)
    
    mock_consent_repo.give_consent.assert_called_once_with(
        123,
        DEFAULT_BASE_LEGAL,
        CURRENT_CONSENT_VERSION
    )


@pytest.mark.asyncio
async def test_revoke_consent(consent_service, mock_consent_repo):
    """Test revoke_consent calls repository"""
    mock_consent_repo.revoke_consent = AsyncMock(return_value=True)
    
    result = await consent_service.revoke_consent(123)
    
    assert result is True
    mock_consent_repo.revoke_consent.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_revoke_consent_fails(consent_service, mock_consent_repo):
    """Test revoke_consent returns False when repository fails"""
    mock_consent_repo.revoke_consent = AsyncMock(return_value=False)
    
    result = await consent_service.revoke_consent(123)
    
    assert result is False


@pytest.mark.asyncio
async def test_consent_version_check(consent_service, mock_consent_repo):
    """Test consent operations respect version"""
    mock_consent_repo.give_consent = AsyncMock()
    
    await consent_service.give_consent(
        user_id=123,
        base_legal="consentimento",
        version="2.0"
    )
    
    mock_consent_repo.give_consent.assert_called_once_with(
        123,
        "consentimento",
        "2.0"
    )


@pytest.mark.asyncio
async def test_consent_service_without_injection():
    """Test ConsentService works without dependency injection (backward compatibility)"""
    service = ConsentService()
    
    # Should not raise error
    assert service.consent_repo is not None

