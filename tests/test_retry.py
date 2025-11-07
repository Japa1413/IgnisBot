"""
Tests for retry logic and circuit breaker.
"""

import pytest
import asyncio
from utils.retry import (
    retry_with_backoff,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError
)


@pytest.mark.asyncio
async def test_retry_success():
    """Test successful retry"""
    call_count = 0
    
    async def success_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = await retry_with_backoff(success_func, max_retries=3)
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_failure():
    """Test retry with failures"""
    call_count = 0
    
    async def failing_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await retry_with_backoff(failing_func, max_retries=2, initial_delay=0.1)
    
    assert call_count == 3  # Initial + 2 retries


def test_circuit_breaker_initial_state():
    """Test circuit breaker initial state"""
    cb = CircuitBreaker()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_circuit_breaker_reset():
    """Test circuit breaker reset"""
    cb = CircuitBreaker()
    cb.failure_count = 5
    cb.state = CircuitState.OPEN
    cb.reset()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

