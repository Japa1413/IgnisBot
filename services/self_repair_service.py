"""
Self-Repair Service - Intelligent bot recovery and health monitoring.

This service provides:
- Auto-restart on crashes
- Health monitoring
- Auto-recovery of connections
- Circuit breaker pattern
- Intelligent error handling
"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime, timedelta
from utils.logger import get_logger
from utils.health_check import HealthCheck

logger = get_logger(__name__)


class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class SelfRepairService:
    """Service for intelligent bot self-repair and monitoring"""
    
    def __init__(self, bot):
        self.bot = bot
        self.restart_count = 0
        self.restart_times: List[datetime] = []
        self.max_restarts_per_hour = 5
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check: Optional[datetime] = None
        self.health_status = ServiceStatus.HEALTHY
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
    
    async def start_monitoring(self):
        """Start health monitoring loop"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Self-repair monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring loop"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Self-repair monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _perform_health_check(self):
        """Perform health check and take action if needed"""
        try:
            health_checker = HealthCheck()
            health_result = await health_checker.get_full_health_report()
            self.last_health_check = datetime.utcnow()
            
            # Determine overall status
            if health_result.get("status") == "healthy":
                self.health_status = ServiceStatus.HEALTHY
            elif health_result.get("status") == "degraded":
                self.health_status = ServiceStatus.DEGRADED
                await self._handle_degraded_health(health_result)
            else:
                self.health_status = ServiceStatus.UNHEALTHY
                await self._handle_unhealthy_health(health_result)
            
            logger.debug(f"Health check completed: {self.health_status.value}")
        except Exception as e:
            logger.error(f"Error performing health check: {e}", exc_info=True)
            self.health_status = ServiceStatus.CRITICAL
    
    async def _handle_degraded_health(self, health_result: Dict):
        """Handle degraded health status"""
        # Try to recover degraded services
        if not health_result.get("database", {}).get("status") == "HEALTHY":
            await self._recover_database()
        
        if not health_result.get("cache", {}).get("status") == "HEALTHY":
            await self._recover_cache()
    
    async def _handle_unhealthy_health(self, health_result: Dict):
        """Handle unhealthy health status"""
        logger.warning("Bot health is UNHEALTHY, attempting recovery...")
        
        # Try to recover critical services
        await self._recover_database()
        await self._recover_cache()
        
        # Check if bot is still connected to Discord
        if not self.bot.is_ready():
            logger.error("Bot is not ready, attempting reconnection...")
            # The bot will handle reconnection automatically, but we log it
    
    async def _recover_database(self):
        """Attempt to recover database connection"""
        try:
            from utils.database import get_pool, close_pool, init_pool
            pool = get_pool()
            if pool is None:
                logger.warning("Database pool is None, reinitializing...")
                await init_pool()
            else:
                # Test connection
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT 1")
            logger.info("Database connection recovered")
        except Exception as e:
            logger.error(f"Failed to recover database: {e}", exc_info=True)
    
    async def _recover_cache(self):
        """Attempt to recover cache"""
        try:
            from utils.cache import CacheService
            cache_service = CacheService()
            # Clear and reinitialize cache
            cache_service.clear_cache()
            logger.info("Cache recovered")
        except Exception as e:
            logger.error(f"Failed to recover cache: {e}", exc_info=True)
    
    def can_restart(self) -> bool:
        """Check if bot can restart (rate limiting)"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Remove old restart times
        self.restart_times = [t for t in self.restart_times if t > hour_ago]
        
        # Check if we've exceeded limit
        if len(self.restart_times) >= self.max_restarts_per_hour:
            return False
        
        return True
    
    def record_restart(self):
        """Record a restart attempt"""
        self.restart_count += 1
        self.restart_times.append(datetime.utcnow())
        logger.warning(f"Restart recorded. Total restarts: {self.restart_count}")
    
    def get_circuit_breaker(self, service_name: str) -> 'CircuitBreaker':
        """Get or create circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(service_name)
        return self.circuit_breakers[service_name]
    
    async def attempt_recovery(self, service_name: str, recovery_func):
        """Attempt to recover a service using circuit breaker pattern"""
        circuit_breaker = self.get_circuit_breaker(service_name)
        
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            logger.warning(f"Circuit breaker for {service_name} is OPEN, skipping recovery")
            return False
        
        try:
            result = await recovery_func()
            circuit_breaker.record_success()
            return result
        except Exception as e:
            circuit_breaker.record_failure()
            logger.error(f"Recovery failed for {service_name}: {e}", exc_info=True)
            return False


class CircuitBreaker:
    """Circuit breaker for service protection"""
    
    def __init__(self, service_name: str, failure_threshold: int = 5, timeout: int = 60):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
    
    def record_success(self):
        """Record a successful operation"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Success in half-open, close the circuit
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit breaker for {self.service_name} CLOSED (recovered)")
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            if self.state == CircuitBreakerState.CLOSED:
                self.state = CircuitBreakerState.OPEN
                logger.error(
                    f"Circuit breaker for {self.service_name} OPENED "
                    f"(failures: {self.failure_count})"
                )
    
    def can_attempt(self) -> bool:
        """Check if we can attempt an operation"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if time_since_failure >= self.timeout:
                    # Move to half-open state
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"Circuit breaker for {self.service_name} moved to HALF_OPEN")
                    return True
            return False
        
        # HALF_OPEN state - allow one attempt
        return True

