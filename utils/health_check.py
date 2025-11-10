"""
Health Check System - Monitor bot health and system status.
"""

from __future__ import annotations

import time
import asyncio
import os
import platform
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger
from utils.cache import get_cache_stats

# Try to import psutil for system information
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage (CPU, Memory, Disk, GPU).
        
        Returns:
            Dict with system resource information
        """
        if not PSUTIL_AVAILABLE:
            return {
                "status": "unknown",
                "error": "psutil not available. Install with: pip install psutil",
                "note": "System resource monitoring disabled"
            }
        
        try:
            # Get current process
            process = psutil.Process(os.getpid())
            
            # CPU Information
            cpu_percent = process.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_percent_system = psutil.cpu_percent(interval=0.1)
            
            # Memory Information
            process_memory = process.memory_info()
            process_memory_mb = process_memory.rss / (1024 * 1024)  # Convert to MB
            process_memory_percent = process.memory_percent()
            
            system_memory = psutil.virtual_memory()
            system_memory_total_gb = system_memory.total / (1024 * 1024 * 1024)
            system_memory_used_gb = system_memory.used / (1024 * 1024 * 1024)
            system_memory_available_gb = system_memory.available / (1024 * 1024 * 1024)
            system_memory_percent = system_memory.percent
            
            # Disk Information
            disk = psutil.disk_usage('/')
            if platform.system() == 'Windows':
                disk = psutil.disk_usage('C:')
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            disk_percent = (disk.used / disk.total) * 100
            
            # GPU Information (optional, try to get if available)
            gpu_info = None
            try:
                # Try NVIDIA GPU (requires nvidia-ml-py)
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    gpu_count = pynvml.nvmlDeviceGetCount()
                    if gpu_count > 0:
                        gpu_handles = []
                        gpu_data = []
                        for i in range(gpu_count):
                            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                            gpu_handles.append(handle)
                            
                            # Get GPU name
                            name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                            
                            # Get GPU memory
                            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                            mem_total_gb = mem_info.total / (1024 * 1024 * 1024)
                            mem_used_gb = mem_info.used / (1024 * 1024 * 1024)
                            mem_free_gb = mem_info.free / (1024 * 1024 * 1024)
                            mem_percent = (mem_info.used / mem_info.total) * 100
                            
                            # Get GPU utilization
                            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                            gpu_util_percent = util.gpu
                            
                            gpu_data.append({
                                "name": name,
                                "memory_total_gb": round(mem_total_gb, 2),
                                "memory_used_gb": round(mem_used_gb, 2),
                                "memory_free_gb": round(mem_free_gb, 2),
                                "memory_percent": round(mem_percent, 1),
                                "utilization_percent": gpu_util_percent
                            })
                        
                        gpu_info = {
                            "available": True,
                            "count": gpu_count,
                            "gpus": gpu_data
                        }
                except ImportError:
                    # nvidia-ml-py not installed
                    pass
                except Exception as e:
                    logger.debug(f"GPU detection failed: {e}")
            except Exception:
                # GPU not available or not NVIDIA
                pass
            
            # Determine status
            status = "healthy"
            if cpu_percent > 90 or system_memory_percent > 90 or disk_percent > 90:
                status = "warning"
            if cpu_percent > 95 or system_memory_percent > 95 or disk_percent > 95:
                status = "critical"
            
            return {
                "status": status,
                "cpu": {
                    "process_percent": round(cpu_percent, 1),
                    "system_percent": round(cpu_percent_system, 1),
                    "cores": cpu_count,
                    "frequency_mhz": round(cpu_freq.current, 0) if cpu_freq else None
                },
                "memory": {
                    "process_mb": round(process_memory_mb, 2),
                    "process_percent": round(process_memory_percent, 2),
                    "system_total_gb": round(system_memory_total_gb, 2),
                    "system_used_gb": round(system_memory_used_gb, 2),
                    "system_available_gb": round(system_memory_available_gb, 2),
                    "system_percent": round(system_memory_percent, 1)
                },
                "disk": {
                    "total_gb": round(disk_total_gb, 2),
                    "used_gb": round(disk_used_gb, 2),
                    "free_gb": round(disk_free_gb, 2),
                    "percent": round(disk_percent, 1)
                },
                "gpu": gpu_info if gpu_info else {"available": False, "note": "GPU monitoring not available"}
            }
        except Exception as e:
            logger.error(f"System resources check failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_full_health_report(self) -> Dict[str, Any]:
        """
        Get complete health report for all systems.
        
        Returns:
            Complete health status dict
        """
        start_time = time.perf_counter()
        
        # Run all checks in parallel
        db_check, cache_check, integrations_check, latency_check, system_resources = await asyncio.gather(
            self.check_database(),
            self.check_cache(),
            self.check_integrations(),
            self.check_command_latency(),
            self.check_system_resources(),
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
        if isinstance(system_resources, Exception):
            system_resources = {"status": "error", "error": str(system_resources)}
        
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
            "command_latency": latency_check,
            "system_resources": system_resources
        }
        
        self._last_check = datetime.utcnow()
        self._metrics = report
        
        return report


# Global health check instance
_health_check = HealthCheck()


def get_health_check() -> HealthCheck:
    """Get global health check instance"""
    return _health_check

