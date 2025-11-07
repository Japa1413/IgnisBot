"""
Bot Monitoring Script - Continuous monitoring and alerting.
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from utils.health_check import get_health_check
from utils.logger import get_logger
from utils.database import initialize_db

logger = get_logger(__name__)

# Monitoring configuration
CHECK_INTERVAL = 300  # 5 minutes
ALERT_THRESHOLD_ERRORS = 10  # Alert after 10 errors
ALERT_THRESHOLD_DEGRADED = 3  # Alert after 3 degraded checks

# Track metrics
_error_count = 0
_degraded_count = 0
_last_alert_time = None


async def check_bot_health():
    """Check bot health and log metrics"""
    global _error_count, _degraded_count, _last_alert_time
    
    try:
        health_check = get_health_check()
        report = await health_check.get_full_health_report()
        
        status = report.get("status", "unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log health status
        if status == "healthy":
            logger.info(f"✅ Health check: {status.upper()} at {timestamp}")
            _degraded_count = 0  # Reset counter
        elif status == "degraded":
            _degraded_count += 1
            logger.warning(f"⚠️ Health check: {status.upper()} at {timestamp} (count: {_degraded_count})")
            
            # Alert if threshold reached
            if _degraded_count >= ALERT_THRESHOLD_DEGRADED:
                await send_alert(f"Bot health is DEGRADED for {_degraded_count} consecutive checks")
                _degraded_count = 0  # Reset after alert
        else:
            _error_count += 1
            logger.error(f"❌ Health check: {status.upper()} at {timestamp} (count: {_error_count})")
            
            # Alert if threshold reached
            if _error_count >= ALERT_THRESHOLD_ERRORS:
                await send_alert(f"Bot health check failed {_error_count} times")
                _error_count = 0  # Reset after alert
        
        # Log detailed metrics
        db_status = report.get("database", {}).get("status", "unknown")
        cache_status = report.get("cache", {}).get("status", "unknown")
        cache_hit_rate = report.get("cache", {}).get("hit_rate", "0%")
        
        logger.debug(
            f"Health metrics - DB: {db_status}, Cache: {cache_status} "
            f"(Hit Rate: {cache_hit_rate})"
        )
        
        return report
        
    except Exception as e:
        _error_count += 1
        logger.error(f"Error in health check monitoring: {e}", exc_info=True)
        return None


async def send_alert(message: str):
    """Send alert notification (can be extended to send Discord message, email, etc.)"""
    global _last_alert_time
    
    # Prevent spam: only alert once per hour
    if _last_alert_time:
        time_since_last = (datetime.now() - _last_alert_time).total_seconds()
        if time_since_last < 3600:  # 1 hour
            return
    
    _last_alert_time = datetime.now()
    logger.critical(f"🚨 ALERT: {message}")
    
    # TODO: Add Discord webhook notification, email, etc.
    # For now, just log to file


async def monitor_loop():
    """Main monitoring loop"""
    logger.info("Starting bot monitoring...")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    
    while True:
        try:
            await check_bot_health()
            await asyncio.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}", exc_info=True)
            await asyncio.sleep(60)  # Wait 1 minute before retrying


async def main():
    """Main entry point"""
    # Initialize database connection
    try:
        await initialize_db()
        logger.info("Database initialized for monitoring")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    # Start monitoring
    await monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())

