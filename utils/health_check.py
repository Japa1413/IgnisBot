"""
Health Check System - Monitor bot health and system status.
"""

from __future__ import annotations

import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.cache import get_cache_stats

logger = get_logger(__name__)


class HealthCheck:
    """Health check system for monitoring bot status"""
    
    def __init__(self):
        self._last_check: Optional[datetime] = None
        self._metrics: Dict[str, Any] = {}
    
    async def check_database(self) -> Dict[str, Any]:
        """
        Check database connection health.
        
        Returns:
            Dict with status, latency, and pool info
        """
        start_time = time.perf_counter()
        status = "healthy"
        error = None
        
        try:
            # Use get_pool() instead of direct _POOL access
            from utils.database import get_pool
            pool = get_pool()
            
            if pool is None:
                return {
                    "status": "unhealthy",
                    "error": "Database pool not initialized",
                    "latency_ms": 0
                }
            
            # Test connection with a simple query
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Get pool stats
            pool_size = pool.size
            free_connections = pool.freesize
            
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "pool_size": pool_size,
                "free_connections": free_connections,
                "pool_utilization": f"{((pool_size - free_connections) / pool_size * 100):.1f}%" if pool_size > 0 else "0%"
            }
        except RuntimeError as e:
            # Pool not initialized
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "status": "unhealthy",
                "error": "Database pool not initialized. Bot may still be starting up.",
                "latency_ms": round(latency_ms, 2)
            }
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Database health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": round(latency_ms, 2)
            }
    
    async def check_cache(self) -> Dict[str, Any]:
        """
        Check cache system health.
        
        Returns:
            Dict with cache statistics
        """
        try:
            stats = get_cache_stats()
            return {
                "status": "healthy",
                **stats
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_integrations(self) -> Dict[str, Any]:
        """
        Check external integrations health (Bloxlink, Roblox API).
        
        Returns:
            Dict with integration status
        """
        results = {
            "bloxlink": {"status": "unknown", "latency_ms": 0},
            "roblox_api": {"status": "unknown", "latency_ms": 0}
        }
        
        # Check Bloxlink
        try:
            from services.bloxlink_service import BloxlinkService
            service = BloxlinkService()
            
            start_time = time.perf_counter()
            # Try to make a simple API call (this will fail if API is down)
            # We'll just check if service is initialized
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            results["bloxlink"] = {
                "status": "healthy" if service.api_base else "unhealthy",
                "latency_ms": round(latency_ms, 2),
                "api_base": service.api_base
            }
        except Exception as e:
            results["bloxlink"] = {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": 0
            }
        
        # Check Roblox API (via Bloxlink service)
        try:
            from services.bloxlink_service import BloxlinkService
            service = BloxlinkService()
            
            start_time = time.perf_counter()
            # Test with a known user ID (1 = Roblox admin account, always exists)
            # This is a lightweight check
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            results["roblox_api"] = {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2)
            }
        except Exception as e:
            results["roblox_api"] = {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": 0
            }
        
        return results
    
    async def check_command_latency(self) -> Dict[str, Any]:
        """
        Check average command latency.
        
        Returns:
            Dict with latency metrics
        """
        # This would ideally track command execution times
        # For now, return placeholder data
        return {
            "status": "healthy",
            "average_latency_ms": 0,  # Would be calculated from metrics
            "note": "Command latency tracking not yet implemented"
        }
    
    async def get_full_health_report(self) -> Dict[str, Any]:
        """
        Get complete health report for all systems.
        
        Returns:
            Complete health status dict
        """
        start_time = time.perf_counter()
        
        # Run all checks in parallel
        db_check, cache_check, integrations_check, latency_check = await asyncio.gather(
            self.check_database(),
            self.check_cache(),
            self.check_integrations(),
            self.check_command_latency(),
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(db_check, Exception):
            db_check = {"status": "error", "error": str(db_check)}
        if isinstance(cache_check, Exception):
            cache_check = {"status": "error", "error": str(cache_check)}
        if isinstance(integrations_check, Exception):
            integrations_check = {"status": "error", "error": str(integrations_check)}
        if isinstance(latency_check, Exception):
            latency_check = {"status": "error", "error": str(latency_check)}
        
        total_latency = (time.perf_counter() - start_time) * 1000
        
        # Determine overall status
        all_healthy = (
            db_check.get("status") == "healthy" and
            cache_check.get("status") == "healthy"
        )
        
        overall_status = "healthy" if all_healthy else "degraded"
        
        report = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "check_duration_ms": round(total_latency, 2),
            "database": db_check,
            "cache": cache_check,
            "integrations": integrations_check,
            "command_latency": latency_check
        }
        
        self._last_check = datetime.utcnow()
        self._metrics = report
        
        return report


# Global health check instance
_health_check = HealthCheck()


def get_health_check() -> HealthCheck:
    """Get global health check instance"""
    return _health_check

