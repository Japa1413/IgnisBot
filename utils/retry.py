"""
Retry Logic with Exponential Backoff and Circuit Breaker Pattern.
"""

from __future__ import annotations

import asyncio
import time
from typing import Callable, Awaitable, TypeVar, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by stopping requests to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> Awaitable[T]:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        
        Returns:
            Function result
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from function
        """
        # Check circuit state
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. Retry after {self.recovery_timeout - elapsed:.0f} seconds"
                    )
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            # If successful, reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker recovered, entering CLOSED state")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker opened after {self.failure_count} failures. "
                    f"Will retry after {self.recovery_timeout} seconds"
                )
            
            raise
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    *args,
    **kwargs
) -> T:
    """
    Retry function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to delay
        *args: Function arguments
        **kwargs: Function keyword arguments
    
    Returns:
        Function result
    
    Raises:
        Exception: Last exception if all retries fail
    """
    import random
    
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                # Calculate delay with exponential backoff
                if jitter:
                    # Add random jitter (±25%)
                    jitter_amount = delay * 0.25 * (random.random() * 2 - 1)
                    actual_delay = delay + jitter_amount
                else:
                    actual_delay = delay
                
                # Cap at max_delay
                actual_delay = min(actual_delay, max_delay)
                
                logger.warning(
                    f"Retry attempt {attempt + 1}/{max_retries} after {actual_delay:.2f}s. "
                    f"Error: {str(e)}"
                )
                
                await asyncio.sleep(actual_delay)
                
                # Calculate next delay
                delay = min(delay * exponential_base, max_delay)
            else:
                logger.error(
                    f"All {max_retries + 1} retry attempts failed. Last error: {str(e)}",
                    exc_info=True
                )
    
    # All retries exhausted
    raise last_exception


async def retry_with_circuit_breaker(
    func: Callable[..., Awaitable[T]],
    circuit_breaker: CircuitBreaker,
    *args,
    **kwargs
) -> T:
    """
    Execute function with circuit breaker and retry logic.
    
    Args:
        func: Async function to execute
        circuit_breaker: Circuit breaker instance
        *args: Function arguments
        **kwargs: Function keyword arguments
    
    Returns:
        Function result
    """
    try:
        return await circuit_breaker.call(func, *args, **kwargs)
    except CircuitBreakerOpenError:
        raise
    except Exception as e:
        # Retry with backoff if not circuit breaker error
        return await retry_with_backoff(func, *args, **kwargs)

