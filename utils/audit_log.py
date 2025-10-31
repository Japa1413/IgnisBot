# utils/audit_log.py
"""
Personal Data Audit System (LGPD Art. 10)

Records all operations performed with personal data for legal compliance.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
import json
import aiomysql
from utils.database import get_pool


async def log_data_operation(
    user_id: int,
    action_type: str,
    data_type: str,
    performed_by: Optional[int] = None,
    purpose: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logs a personal data operation in the database.
    
    Action types:
        - CREATE: Record creation
        - READ: Data reading
        - UPDATE: Data update
        - DELETE: Data deletion
        - EXPORT: Data export
        - ACCESS: General data access
    
    Args:
        user_id: ID of user whose data was manipulated
        action_type: Type of action performed
        data_type: Data type (user_data, points, rank, consent, etc.)
        performed_by: ID of user/admin who performed the action (None = user themselves)
        purpose: Purpose of the operation (e.g.: "Points update for event")
        details: Additional details in dict format (will be serialized as JSON)
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    details_json = json.dumps(details) if details else None
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO data_audit_log 
                (user_id, action_type, data_type, performed_by, purpose, details, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                user_id,
                action_type,
                data_type,
                performed_by,
                purpose,
                details_json
            ))


async def get_user_audit_history(
    user_id: int,
    limit: int = 100
) -> list[Dict[str, Any]]:
    """
    Get audit history for a user.
    
    Args:
        user_id: User ID
        limit: Maximum number of records to return
    
    Returns:
        List of audit records ordered by timestamp (most recent first)
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
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
            """, (user_id, limit))
            
            results = await cursor.fetchall()
            
            # Parse JSON details
            for record in results:
                if record.get("details"):
                    try:
                        record["details"] = json.loads(record["details"])
                    except (json.JSONDecodeError, TypeError):
                        record["details"] = {}
            
            return results


async def delete_user_audit_logs(user_id: int) -> int:
    """
    Remove all audit logs for a user (used when user exercises right to be forgotten).
    
    Args:
        user_id: User ID
    
    Returns:
        Number of deleted records
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                DELETE FROM data_audit_log
                WHERE user_id = %s
            """, (user_id,))
            
            return cursor.rowcount

