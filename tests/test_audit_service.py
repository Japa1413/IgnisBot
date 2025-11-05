"""
Tests for AuditService.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from domain.protocols import AuditRepositoryProtocol
from services.audit_service import AuditService


@pytest.fixture
def mock_audit_repo():
    """Mock audit repository"""
    return MagicMock(spec=AuditRepositoryProtocol)


@pytest.fixture
def audit_service(mock_audit_repo):
    """AuditService instance with mocked dependencies"""
    return AuditService(audit_repo=mock_audit_repo)


@pytest.mark.asyncio
async def test_log_operation(audit_service, mock_audit_repo):
    """Test log_operation calls repository with correct parameters"""
    mock_audit_repo.create = AsyncMock()
    
    await audit_service.log_operation(
        user_id=123,
        action_type="UPDATE",
        data_type="points",
        performed_by=456,
        purpose="Test operation",
        details={"amount": 50}
    )
    
    mock_audit_repo.create.assert_called_once_with(
        user_id=123,
        action_type="UPDATE",
        data_type="points",
        performed_by=456,
        purpose="Test operation",
        details={"amount": 50}
    )


@pytest.mark.asyncio
async def test_log_operation_minimal(audit_service, mock_audit_repo):
    """Test log_operation with minimal required parameters"""
    mock_audit_repo.create = AsyncMock()
    
    await audit_service.log_operation(
        user_id=123,
        action_type="READ",
        data_type="user_data"
    )
    
    mock_audit_repo.create.assert_called_once_with(
        user_id=123,
        action_type="READ",
        data_type="user_data",
        performed_by=None,
        purpose=None,
        details=None
    )


@pytest.mark.asyncio
async def test_log_operation_with_details(audit_service, mock_audit_repo):
    """Test log_operation with additional details"""
    mock_audit_repo.create = AsyncMock()
    
    details = {
        "before": 100,
        "after": 150,
        "delta": 50,
        "reason": "Test reason"
    }
    
    await audit_service.log_operation(
        user_id=123,
        action_type="UPDATE",
        data_type="points",
        details=details
    )
    
    mock_audit_repo.create.assert_called_once()
    call_kwargs = mock_audit_repo.create.call_args[1]
    assert call_kwargs["details"] == details


@pytest.mark.asyncio
async def test_log_operation_performed_by(audit_service, mock_audit_repo):
    """Test log_operation records performer"""
    mock_audit_repo.create = AsyncMock()
    
    await audit_service.log_operation(
        user_id=123,
        action_type="DELETE",
        data_type="user_data",
        performed_by=789
    )
    
    mock_audit_repo.create.assert_called_once()
    call_kwargs = mock_audit_repo.create.call_args[1]
    assert call_kwargs["performed_by"] == 789


@pytest.mark.asyncio
async def test_log_operation_error_handling(audit_service, mock_audit_repo):
    """Test log_operation handles repository errors gracefully"""
    from utils.logger import get_logger
    
    mock_audit_repo.create = AsyncMock(side_effect=Exception("Database error"))
    
    # Should not raise - audit failures shouldn't break operations
    await audit_service.log_operation(
        user_id=123,
        action_type="UPDATE",
        data_type="points"
    )
    
    mock_audit_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_history(audit_service, mock_audit_repo):
    """Test get_user_history returns audit records"""
    expected_history = [
        {"id": 1, "user_id": 123, "action_type": "UPDATE", "timestamp": "2025-10-31"},
        {"id": 2, "user_id": 123, "action_type": "READ", "timestamp": "2025-10-30"}
    ]
    mock_audit_repo.get_history = AsyncMock(return_value=expected_history)
    
    result = await audit_service.get_user_history(user_id=123, limit=100)
    
    assert result == expected_history
    mock_audit_repo.get_history.assert_called_once_with(123, 100)


@pytest.mark.asyncio
async def test_get_user_history_limit(audit_service, mock_audit_repo):
    """Test get_user_history respects limit parameter"""
    mock_audit_repo.get_history = AsyncMock(return_value=[])
    
    await audit_service.get_user_history(user_id=123, limit=50)
    
    mock_audit_repo.get_history.assert_called_once_with(123, 50)


@pytest.mark.asyncio
async def test_delete_user_history(audit_service, mock_audit_repo):
    """Test delete_user_history calls repository and returns count"""
    mock_audit_repo.delete_user_logs = AsyncMock(return_value=5)
    
    result = await audit_service.delete_user_history(user_id=123)
    
    assert result == 5
    mock_audit_repo.delete_user_logs.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_audit_service_without_injection():
    """Test AuditService works without dependency injection (backward compatibility)"""
    service = AuditService()
    
    # Should not raise error
    assert service.audit_repo is not None

