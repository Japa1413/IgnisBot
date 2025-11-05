#!/usr/bin/env python3
"""
Validation Script: Verificar se validação de consentimento está funcionando

Este script testa se a validação de consentimento está implementada corretamente
em todas as operações de pontos.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.points_service import PointsService
from services.consent_service import ConsentService
from unittest.mock import AsyncMock, MagicMock
import asyncio


async def test_consent_validation():
    """Test if consent validation is working"""
    print("Testing consent validation in PointsService...")
    
    # Mock bot
    bot = MagicMock()
    
    # Create service
    service = PointsService(bot)
    
    # Mock repository
    service.user_repo = AsyncMock()
    service.consent_service = AsyncMock()
    
    # Test 1: add_points without consent should raise ValueError
    print("\n1. Testing add_points without consent...")
    service.consent_service.has_consent = AsyncMock(return_value=False)
    
    try:
        await service.add_points(
            user_id=123,
            amount=10,
            reason="test",
            performed_by=456
        )
        print("❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        if "consent" in str(e).lower():
            print("✅ PASSED: ValueError raised for missing consent")
        else:
            print(f"❌ FAILED: Wrong error message: {e}")
            return False
    
    # Test 2: add_points with consent should work
    print("\n2. Testing add_points with consent...")
    service.consent_service.has_consent = AsyncMock(return_value=True)
    service.user_repo.get_or_create = AsyncMock(return_value={"points": 100})
    service.user_repo.update_points = AsyncMock(return_value=110)
    
    try:
        result = await service.add_points(
            user_id=123,
            amount=10,
            reason="test",
            performed_by=456
        )
        if result.after == 110:
            print("✅ PASSED: Points added successfully with consent")
        else:
            print("❌ FAILED: Wrong result")
            return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False
    
    # Test 3: remove_points without consent should raise ValueError
    print("\n3. Testing remove_points without consent...")
    service.consent_service.has_consent = AsyncMock(return_value=False)
    
    try:
        await service.remove_points(
            user_id=123,
            amount=10,
            reason="test",
            performed_by=456
        )
        print("❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        if "consent" in str(e).lower():
            print("✅ PASSED: ValueError raised for missing consent")
        else:
            print(f"❌ FAILED: Wrong error message: {e}")
            return False
    
    print("\n✅ All consent validation tests passed!")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_consent_validation())
    sys.exit(0 if result else 1)

