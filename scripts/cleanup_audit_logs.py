#!/usr/bin/env python3
"""
Cleanup Script for Audit Logs - LGPD Compliance

Automatically removes audit logs older than 6 months as per LGPD Art. 15
(Data Retention Policy).

This script should be run periodically (e.g., daily via cron).

Usage:
    python scripts/cleanup_audit_logs.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import get_pool, initialize_db
from utils.logger import get_logger
from utils.config import DB_NAME

logger = get_logger(__name__)

# Retention period: 6 months
RETENTION_DAYS = 180
RETENTION_PERIOD = timedelta(days=RETENTION_DAYS)


async def cleanup_old_audit_logs():
    """
    Remove audit logs older than retention period (6 months).
    
    Returns:
        Number of deleted records
    """
    pool = get_pool()
    cutoff_date = datetime.utcnow() - RETENTION_PERIOD
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Count records to be deleted
            await cursor.execute(
                """
                SELECT COUNT(*) 
                FROM data_audit_log 
                WHERE timestamp < %s
                """,
                (cutoff_date,)
            )
            count_result = await cursor.fetchone()
            records_to_delete = count_result[0] if count_result else 0
            
            if records_to_delete == 0:
                logger.info("No audit logs to clean up")
                return 0
            
            # Delete old records
            await cursor.execute(
                """
                DELETE FROM data_audit_log 
                WHERE timestamp < %s
                """,
                (cutoff_date,)
            )
            
            deleted_count = cursor.rowcount
            
            logger.info(
                f"Cleaned up {deleted_count} audit log records older than {RETENTION_DAYS} days "
                f"(cutoff: {cutoff_date.isoformat()})"
            )
            
            return deleted_count


async def main():
    """Main entry point"""
    try:
        # Initialize database connection
        await initialize_db()
        
        # Clean up old logs
        deleted = await cleanup_old_audit_logs()
        
        if deleted > 0:
            print(f"✅ Successfully deleted {deleted} old audit log records")
        else:
            print("✅ No old audit logs to clean up")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during audit log cleanup: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

