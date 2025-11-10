"""
Company Mapping Service - Maps Roblox ranks to company numbers.

This service determines which company a user belongs to based on their
Roblox rank in the main group (6340169).
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from utils.logger import get_logger
from services.roblox_groups_service import get_roblox_groups_service

logger = get_logger(__name__)

# Main group ID
MAIN_GROUP_ID = 6340169

# Rank to Company mapping
# Format: {rank_number: company_number}
# This will be configurable in the future
RANK_TO_COMPANY_MAP: Dict[int, int] = {
    # Example mappings - to be configured by user
    # Rank 1-10: Company 1
    # Rank 11-20: Company 2
    # etc.
}

# Rank name to Company mapping (alternative)
# Format: {"rank_name": company_number}
RANK_NAME_TO_COMPANY_MAP: Dict[str, int] = {
    # Example mappings - to be configured by user
    # "Legionary": 6,
    # "Captain": 1,
    # etc.
}


class CompanyMappingService:
    """
    Service for mapping Roblox ranks to company numbers.
    
    This determines which company a user belongs to based on their
    rank in the main Roblox group.
    """
    
    def __init__(self):
        """Initialize Company Mapping service"""
        self.groups_service = get_roblox_groups_service()
    
    async def get_company_for_user(
        self,
        roblox_id: int,
        roblox_username: Optional[str] = None
    ) -> Optional[int]:
        """
        Get company number for a user based on their Roblox rank.
        
        Args:
            roblox_id: Roblox user ID
            roblox_username: Optional Roblox username (for logging)
        
        Returns:
            Company number (1-10) or None if not determinable
        """
        try:
            # Get user's rank in main group
            rank_info = await self.groups_service.get_user_rank_in_group(
                roblox_id,
                MAIN_GROUP_ID
            )
            
            if not rank_info:
                logger.debug(
                    f"User {roblox_username or roblox_id} not in main group {MAIN_GROUP_ID}"
                )
                return None
            
            rank_number = rank_info.get("rank", 0)
            rank_name = rank_info.get("role", "")
            
            # Try rank name mapping first (more precise)
            if rank_name and rank_name in RANK_NAME_TO_COMPANY_MAP:
                company = RANK_NAME_TO_COMPANY_MAP[rank_name]
                logger.debug(
                    f"Company determined by rank name '{rank_name}': {company} "
                    f"for user {roblox_username or roblox_id}"
                )
                return company
            
            # Try rank number mapping
            if rank_number in RANK_TO_COMPANY_MAP:
                company = RANK_TO_COMPANY_MAP[rank_number]
                logger.debug(
                    f"Company determined by rank number {rank_number}: {company} "
                    f"for user {roblox_username or roblox_id}"
                )
                return company
            
            # Default: no company determined
            logger.debug(
                f"No company mapping found for rank {rank_number} ({rank_name}) "
                f"for user {roblox_username or roblox_id}"
            )
            return None
        
        except Exception as e:
            logger.error(
                f"Error determining company for user {roblox_username or roblox_id}: {e}",
                exc_info=True
            )
            return None
    
    def set_rank_to_company_mapping(self, rank_number: int, company: int):
        """
        Set a mapping from rank number to company.
        
        Args:
            rank_number: Roblox rank number
            company: Company number (1-10)
        """
        if company < 1 or company > 10:
            raise ValueError("Company must be between 1 and 10")
        
        RANK_TO_COMPANY_MAP[rank_number] = company
        logger.info(f"Set rank {rank_number} -> company {company}")
    
    def set_rank_name_to_company_mapping(self, rank_name: str, company: int):
        """
        Set a mapping from rank name to company.
        
        Args:
            rank_name: Roblox rank name (role name)
            company: Company number (1-10)
        """
        if company < 1 or company > 10:
            raise ValueError("Company must be between 1 and 10")
        
        RANK_NAME_TO_COMPANY_MAP[rank_name] = company
        logger.info(f"Set rank name '{rank_name}' -> company {company}")
    
    def get_all_mappings(self) -> Dict[str, Any]:
        """
        Get all current mappings.
        
        Returns:
            Dict with rank_to_company and rank_name_to_company mappings
        """
        return {
            "rank_to_company": RANK_TO_COMPANY_MAP.copy(),
            "rank_name_to_company": RANK_NAME_TO_COMPANY_MAP.copy()
        }


# Singleton instance
_company_mapping_service: Optional[CompanyMappingService] = None


def get_company_mapping_service() -> CompanyMappingService:
    """Get singleton CompanyMappingService instance"""
    global _company_mapping_service
    if _company_mapping_service is None:
        _company_mapping_service = CompanyMappingService()
    return _company_mapping_service


