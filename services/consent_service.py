"""
Consent Service - Business logic for consent operations.
"""

from __future__ import annotations

from typing import Optional, Dict
from repositories.consent_repository import ConsentRepository
from domain.protocols import ConsentRepositoryProtocol
from utils.consent_manager import CURRENT_CONSENT_VERSION, DEFAULT_BASE_LEGAL
from utils.logger import get_logger

logger = get_logger(__name__)


class ConsentService:
    """Service for consent-related business logic"""
    
    def __init__(self, consent_repo: Optional[ConsentRepositoryProtocol] = None):
        """
        Initialize consent service.
        
        Args:
            consent_repo: Consent repository (injected, defaults to ConsentRepository)
        """
        # Dependency injection with default for backward compatibility
        self.consent_repo = consent_repo or ConsentRepository()
    
    async def has_consent(self, user_id: int) -> bool:
        """
        Check if user has given consent.
        
        Args:
            user_id: User ID
        
        Returns:
            True if user has consent
        """
        return await self.consent_repo.has_consent(user_id)
    
    async def give_consent(
        self,
        user_id: int,
        base_legal: str = DEFAULT_BASE_LEGAL,
        version: str = CURRENT_CONSENT_VERSION
    ) -> None:
        """
        Record user consent.
        
        Args:
            user_id: User ID
            base_legal: Legal basis
            version: Privacy policy version
        """
        await self.consent_repo.give_consent(user_id, base_legal, version)
    
    async def revoke_consent(self, user_id: int) -> bool:
        """
        Revoke user consent.
        
        Args:
            user_id: User ID
        
        Returns:
            True if consent was revoked
        """
        return await self.consent_repo.revoke_consent(user_id)
    
    async def get_info(self, user_id: int) -> Optional[Dict]:
        """
        Get consent information.
        
        Args:
            user_id: User ID
        
        Returns:
            Consent info dict or None
        """
        return await self.consent_repo.get(user_id)
    
    async def check_required(self, user_id: int) -> bool:
        """
        Check if user needs to give consent.
        
        Returns True if:
        - No consent record exists, OR
        - Consent was given in old policy version
        
        Args:
            user_id: User ID
        
        Returns:
            True if consent is required
        """
        consent_info = await self.get_info(user_id)
        
        if not consent_info:
            return True  # No record = needs to give consent
        
        if not consent_info.get("consent_given", False):
            return True  # Consent revoked
        
        # Check if consent version is up to date
        consent_version = consent_info.get("consent_version", "0.0")
        return consent_version != CURRENT_CONSENT_VERSION

