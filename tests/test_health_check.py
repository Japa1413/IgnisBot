"""
Tests for health check system.
"""

import pytest
from utils.health_check import HealthCheck


@pytest.mark.asyncio
async def test_health_check_initialization():
    """Test health check initialization"""
    hc = HealthCheck()
    assert hc._last_check is None
    assert isinstance(hc._metrics, dict)


@pytest.mark.asyncio
async def test_cache_check():
    """Test cache health check"""
    hc = HealthCheck()
    result = await hc.check_cache()
    assert "status" in result
    assert result["status"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
async def test_full_health_report():
    """Test full health report generation"""
    hc = HealthCheck()
    report = await hc.get_full_health_report()
    assert "status" in report
    assert "timestamp" in report
    assert "database" in report
    assert "cache" in report
    assert "integrations" in report

