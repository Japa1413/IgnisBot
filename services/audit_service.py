"""
Audit Service - Business logic for audit operations.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from repositories.audit_repository import AuditRepository
from domain.protocols import AuditRepositoryProtocol
from utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for audit-related business logic"""
    
    def __init__(self, audit_repo: Optional[AuditRepositoryProtocol] = None):
        """
        Initialize audit service.
        
        Args:
            audit_repo: Audit repository (injected, defaults to AuditRepository)
        """
        # Dependency injection with default for backward compatibility
        self.audit_repo = audit_repo or AuditRepository()
    
    async def log_operation(
        self,
        user_id: int,
        action_type: str,
        data_type: str,
        performed_by: Optional[int] = None,
        purpose: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an audit operation (fire-and-forget, non-blocking).
        
        This should be called via asyncio.create_task() in most cases
        to avoid blocking the main operation.
        
        Args:
            user_id: ID of user whose data was manipulated
            action_type: Action type (CREATE, READ, UPDATE, DELETE, etc.)
            data_type: Data type (user_data, points, rank, etc.)
            performed_by: ID of user who performed action
            purpose: Purpose of the operation
            details: Additional details
        """
        try:
            await self.audit_repo.create(
                user_id=user_id,
                action_type=action_type,
                data_type=data_type,
                performed_by=performed_by,
                purpose=purpose,
                details=details
            )
        except Exception as e:
            logger.error(f"Error logging audit operation: {e}", exc_info=True)
            # Don't raise - audit failures shouldn't break main operations
    
    async def get_user_history(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
        
        Returns:
            List of audit records
        """
        return await self.audit_repo.get_history(user_id, limit)
    
    async def delete_user_history(self, user_id: int) -> int:
        """
        Delete all audit logs for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Number of deleted records
        """
        return await self.audit_repo.delete_user_logs(user_id)

