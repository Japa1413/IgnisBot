"""
Setup Backup Scheduler - Configure automatic database backups.
"""

import asyncio
from utils.backup import schedule_backups, create_backup, cleanup_old_backups
from utils.database import initialize_db
from utils.logger import get_logger

logger = get_logger(__name__)


async def setup_backup_scheduler(interval_hours: int = 24):
    """
    Setup automatic backup scheduler.
    
    Args:
        interval_hours: Hours between backups (default: 24)
    """
    logger.info(f"Setting up backup scheduler (interval: {interval_hours} hours)")
    
    # Initialize database
    await initialize_db()
    
    # Create initial backup
    logger.info("Creating initial backup...")
    backup_path = await create_backup()
    if backup_path:
        logger.info(f"Initial backup created: {backup_path}")
    else:
        logger.warning("Failed to create initial backup")
    
    # Cleanup old backups
    await cleanup_old_backups()
    
    # Start scheduled backups
    logger.info("Starting backup scheduler...")
    await schedule_backups(interval_hours)


async def main():
    """Main entry point"""
    import sys
    
    # Get interval from command line or use default
    interval_hours = 24
    if len(sys.argv) > 1:
        try:
            interval_hours = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid interval: {sys.argv[1]}. Using default: 24 hours")
    
    await setup_backup_scheduler(interval_hours)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Backup scheduler stopped by user")

