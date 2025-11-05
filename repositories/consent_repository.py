"""
Consent Repository - Data access for consent operations.
"""

from __future__ import annotations

from typing import Optional, Dict
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class ConsentRepository(BaseRepository):
    """Repository for consent data access"""
    
    async def get(self, user_id: int) -> Optional[Dict]:
        """
        Get consent information for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Consent info dict or None if not found
        """
        return await self.execute_query(
            """
            SELECT 
                user_id,
                consent_date,
                consent_version,
                base_legal,
                consent_given,
                updated_at
            FROM user_consent
            WHERE user_id = %s
            """,
            (user_id,),
            fetch_one=True,
            as_dict=True
        )
    
    async def has_consent(self, user_id: int) -> bool:
        """
        Check if user has given consent.
        
        Args:
            user_id: User ID
        
        Returns:
            True if user has consent
        """
        result = await self.execute_query(
            "SELECT consent_given FROM user_consent WHERE user_id = %s",
            (user_id,),
            fetch_one=True
        )
        
        return result and result[0] if result else False
    
    async def give_consent(
        self,
        user_id: int,
        base_legal: str = "consentimento",
        version: str = "1.0"
    ) -> None:
        """
        Record user consent.
        
        Args:
            user_id: User ID
            base_legal: Legal basis (default: "consentimento")
            version: Privacy policy version
        """
        await self.execute_query(
            """
            INSERT INTO user_consent 
            (user_id, consent_date, consent_version, base_legal, consent_given)
            VALUES (%s, NOW(), %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE
                consent_date = NOW(),
                consent_version = %s,
                base_legal = %s,
                consent_given = TRUE,
                updated_at = NOW()
            """,
            (user_id, version, base_legal, version, base_legal)
        )
    
    async def revoke_consent(self, user_id: int) -> bool:
        """
        Revoke user consent.
        
        Args:
            user_id: User ID
        
        Returns:
            True if consent was revoked successfully
        """
        rowcount = await self.execute_query(
            """
            UPDATE user_consent
            SET consent_given = FALSE,
                updated_at = NOW()
            WHERE user_id = %s
            """,
            (user_id,)
        )
        
        return (rowcount or 0) > 0
