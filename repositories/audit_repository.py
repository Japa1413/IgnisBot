"""
Audit Repository - Data access for audit log operations.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
import json
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class AuditRepository(BaseRepository):
    """Repository for audit log data access"""
    
    async def create(
        self,
        user_id: int,
        action_type: str,
        data_type: str,
        performed_by: Optional[int] = None,
        purpose: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create audit log entry.
        
        Args:
            user_id: ID of user whose data was manipulated
            action_type: Action type (CREATE, READ, UPDATE, DELETE, etc.)
            data_type: Data type (user_data, points, rank, etc.)
            performed_by: ID of user who performed action (None = user themselves)
            purpose: Purpose of the operation
            details: Additional details as dict (will be serialized as JSON)
        """
        details_json = json.dumps(details) if details else None
        
        await self.execute_query(
            """
            INSERT INTO data_audit_log 
            (user_id, action_type, data_type, performed_by, purpose, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (user_id, action_type, data_type, performed_by, purpose, details_json)
        )
    
    async def get_history(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
        
        Returns:
            List of audit records ordered by timestamp (most recent first)
        """
        results = await self.execute_query(
            """
            SELECT 
                id,
                user_id,
                action_type,
                data_type,
                performed_by,
                purpose,
                timestamp,
                details
            FROM data_audit_log
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (user_id, limit),
            fetch_all=True,
            as_dict=True
        )
        
        # Parse JSON details
        if results:
            for record in results:
                if record.get("details"):
                    try:
                        record["details"] = json.loads(record["details"])
                    except (json.JSONDecodeError, TypeError):
                        record["details"] = {}
        
        return results or []
    
    async def delete_user_logs(self, user_id: int) -> int:
        """
        Delete all audit logs for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Number of deleted records
        """
        rowcount = await self.execute_query(
            "DELETE FROM data_audit_log WHERE user_id = %s",
            (user_id,)
        )
        return rowcount or 0
