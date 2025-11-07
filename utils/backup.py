"""
Backup System - Automated database backups.
"""

from __future__ import annotations

import asyncio
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from utils.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from utils.logger import get_logger

logger = get_logger(__name__)

# Backup directory
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

# Retention: 7 days
BACKUP_RETENTION_DAYS = 7


async def create_backup() -> Optional[str]:
    """
    Create a database backup.
    
    Returns:
        Path to backup file or None if failed
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"ignis_backup_{timestamp}.sql"
        backup_path = BACKUP_DIR / backup_filename
        
        # Use mysqldump to create backup
        cmd = [
            "mysqldump",
            f"--host={DB_HOST}",
            f"--user={DB_USER}",
            f"--password={DB_PASSWORD}",
            "--single-transaction",
            "--routines",
            "--triggers",
            DB_NAME
        ]
        
        # Execute mysqldump
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Backup failed: {stderr.decode()}")
            return None
        
        # Write backup to file
        with open(backup_path, "wb") as f:
            f.write(stdout)
        
        # Compress backup (optional, using gzip)
        try:
            import gzip
            compressed_path = backup_path.with_suffix(".sql.gz")
            with open(backup_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    f_out.writelines(f_in)
            # Remove uncompressed file
            backup_path.unlink()
            backup_path = compressed_path
        except ImportError:
            logger.warning("gzip not available, backup not compressed")
        
        logger.info(f"Backup created: {backup_path}")
        return str(backup_path)
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}", exc_info=True)
        return None


async def cleanup_old_backups():
    """
    Remove backups older than retention period.
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
        
        deleted_count = 0
        for backup_file in BACKUP_DIR.glob("ignis_backup_*"):
            # Get file modification time
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if mtime < cutoff_date:
                backup_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old backup: {backup_file}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old backup(s)")
        
    except Exception as e:
        logger.error(f"Error cleaning up backups: {e}", exc_info=True)


async def restore_backup(backup_path: str) -> bool:
    """
    Restore database from backup.
    
    Args:
        backup_path: Path to backup file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if file exists
        backup_file = Path(backup_path)
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Decompress if needed
        if backup_file.suffix == ".gz":
            import gzip
            decompressed_path = backup_file.with_suffix("")
            with gzip.open(backup_file, "rb") as f_in:
                with open(decompressed_path, "wb") as f_out:
                    f_out.writelines(f_in)
            backup_file = decompressed_path
        
        # Read backup file
        with open(backup_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Execute SQL
        from utils.database import get_pool
        pool = get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Split by semicolon and execute each statement
                statements = [s.strip() for s in sql_content.split(";") if s.strip()]
                for statement in statements:
                    if statement:
                        await cursor.execute(statement)
                await conn.commit()
        
        logger.info(f"Backup restored from: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error restoring backup: {e}", exc_info=True)
        return False


async def schedule_backups(interval_hours: int = 24):
    """
    Schedule automatic backups.
    
    Args:
        interval_hours: Hours between backups (default: 24)
    """
    while True:
        try:
            await asyncio.sleep(interval_hours * 3600)  # Convert to seconds
            await create_backup()
            await cleanup_old_backups()
        except Exception as e:
            logger.error(f"Error in backup scheduler: {e}", exc_info=True)
            await asyncio.sleep(3600)  # Wait 1 hour before retrying

