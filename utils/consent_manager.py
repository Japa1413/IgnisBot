# utils/consent_manager.py
"""
LGPD Consent Manager

Manages user consent for personal data processing,
according to LGPD (Art. 7º, I) and GDPR (Art. 6º, 1(a)) requirements.
"""

from __future__ import annotations

from typing import Optional, Dict
from datetime import datetime
import aiomysql
from utils.database import get_pool

# Current privacy policy version
CURRENT_CONSENT_VERSION = "1.0"

# Default legal basis (can be changed as needed)
DEFAULT_BASE_LEGAL = "consentimento"  # LGPD Art. 7º, I


async def has_consent(user_id: int) -> bool:
    """
    Checks if user has given consent for data processing.
    
    Args:
        user_id: User ID
    
    Returns:
        True if user gave consent, False otherwise
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT consent_given
                FROM user_consent
                WHERE user_id = %s
            """, (user_id,))
            
            result = await cursor.fetchone()
            return result and result.get("consent_given", False)


async def give_consent(
    user_id: int,
    base_legal: str = DEFAULT_BASE_LEGAL,
    version: str = CURRENT_CONSENT_VERSION
) -> bool:
    """
    Records user consent for data processing.
    
    Args:
        user_id: User ID
        base_legal: Legal basis for processing (default: "consentimento")
        version: Accepted privacy policy version
    
    Returns:
        True if consent was recorded successfully
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Use INSERT ... ON DUPLICATE KEY UPDATE for upsert
            await cursor.execute("""
                INSERT INTO user_consent 
                (user_id, consent_date, consent_version, base_legal, consent_given)
                VALUES (%s, NOW(), %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE
                    consent_date = NOW(),
                    consent_version = %s,
                    base_legal = %s,
                    consent_given = TRUE,
                    updated_at = NOW()
            """, (user_id, version, base_legal, version, base_legal))
            
            return True


async def revoke_consent(user_id: int) -> bool:
    """
    Revokes user consent (LGPD Art. 18, VI).
    
    When consent is revoked, data may still be retained
    if there is another applicable legal basis (e.g.: legal obligation fulfillment).
    Complete deletion must be done via delete_user_data().
    
    Args:
        user_id: User ID
    
    Returns:
        True if consent was revoked successfully
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                UPDATE user_consent
                SET consent_given = FALSE,
                    updated_at = NOW()
                WHERE user_id = %s
            """, (user_id,))
            
            return cursor.rowcount > 0


async def get_consent_info(user_id: int) -> Optional[Dict]:
    """
    Get user consent information.
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with consent information or None if not found
    
    Raises:
        RuntimeError: If database pool is not initialized
    """
    pool = get_pool()
    
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT 
                    user_id,
                    consent_date,
                    consent_version,
                    base_legal,
                    consent_given,
                    updated_at
                FROM user_consent
                WHERE user_id = %s
            """, (user_id,))
            
            return await cursor.fetchone()


async def check_consent_required(user_id: int) -> bool:
    """
    Checks if user needs to give consent.
    
    Returns True if:
    - User has no consent record, OR
    - Consent was given in old policy version
    
    Args:
        user_id: User ID
    
    Returns:
        True if consent is required
    """
    consent_info = await get_consent_info(user_id)
    
    if not consent_info:
        return True  # No record = needs to give consent
    
    if not consent_info.get("consent_given", False):
        return True  # Consent revoked
    
    # Check if consent version is up to date
    consent_version = consent_info.get("consent_version", "0.0")
    return consent_version != CURRENT_CONSENT_VERSION

