"""
Roblox Outfits Service - Integration with Roblox Avatar/Outfits API.

This service handles all interactions with Roblox Outfits API to retrieve:
- User's saved outfits
- Outfit details (items, colors, scale)
- Outfit thumbnails
"""

from __future__ import annotations

import aiohttp
from typing import Optional, Dict, Any, List
from utils.logger import get_logger
from utils.retry import retry_with_backoff, CircuitBreaker, CircuitBreakerOpenError

logger = get_logger(__name__)

# Circuit breaker for Roblox Outfits API
_roblox_outfits_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=aiohttp.ClientError
)


class RobloxOutfitsService:
    """Service for Roblox Outfits API integration"""
    
    def __init__(self):
        """Initialize Roblox Outfits service"""
        # Roblox Avatar API base URL
        self.api_base = "https://avatar.roblox.com/v1"
        # Roblox Thumbnails API base URL
        self.thumbnails_api_base = "https://thumbnails.roblox.com/v1"
    
    async def get_user_outfits(self, roblox_user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all saved outfits for a user.
        
        Args:
            roblox_user_id: Roblox user ID
            limit: Maximum number of outfits to retrieve (default: 50)
        
        Returns:
            List of outfits with:
            - id: Outfit ID
            - name: Outfit name
            - isEditable: Whether outfit is editable
            - thumbnail_url: URL to outfit thumbnail (if available)
        """
        try:
            url = f"{self.api_base}/users/{roblox_user_id}/outfits"
            params = {
                "page": 1,
                "itemsPerPage": limit
            }
            
            logger.info(f"[OUTFITS HARD TEST] Fetching outfits from: {url} with params: {params}")
            
            async def _fetch():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        logger.info(f"[OUTFITS HARD TEST] Response status: {response.status}")
                        
                        if response.status == 404:
                            logger.warning(f"[OUTFITS HARD TEST] User {roblox_user_id} not found or has no outfits")
                            return []
                        
                        if response.status != 200:
                            response_text = await response.text()
                            logger.warning(f"[OUTFITS HARD TEST] API returned status {response.status}: {response_text[:500]}")
                            return []
                        
                        data = await response.json()
                        logger.info(f"[OUTFITS HARD TEST] Response data keys: {list(data.keys())}")
                        
                        all_outfits = data.get("data", [])
                        logger.info(f"[OUTFITS HARD TEST] Found {len(all_outfits)} total outfits in response")
                        
                        # Filter ONLY user-created outfits (isEditable: True)
                        # These are the "Saved Outfits" created by the user in Characters > Creations
                        user_created_outfits = [outfit for outfit in all_outfits if outfit.get("isEditable", False)]
                        logger.info(f"[OUTFITS HARD TEST] Filtered to {len(user_created_outfits)} user-created outfits (isEditable: True)")
                        
                        # Log first outfit structure for debugging
                        if user_created_outfits:
                            logger.info(f"[OUTFITS HARD TEST] First user-created outfit structure: {list(user_created_outfits[0].keys())}")
                            logger.info(f"[OUTFITS HARD TEST] First user-created outfit data: {user_created_outfits[0]}")
                        
                        # Generate thumbnail URLs for user-created outfits only
                        # We'll try multiple URL formats as fallback strategies
                        if user_created_outfits:
                            for outfit in user_created_outfits:
                                outfit_id = outfit.get("id")
                                outfit_name = outfit.get("name", "Unknown")
                                if outfit_id:
                                    # Strategy 1: Use Roblox Thumbnails API with outfit ID
                                    # Note: This API may require the outfit to be public or may not work for all outfits
                                    thumbnail_url = f"https://thumbnails.roblox.com/v1/users/outfit-3d?userOutfitIds={outfit_id}&size=420x420&format=Png&isCircular=false"
                                    outfit["thumbnail_url"] = thumbnail_url
                                    outfit["thumbnail_url_fallback"] = f"https://thumbnails.roblox.com/v1/users/outfit?userOutfitIds={outfit_id}&size=420x420&format=Png"
                                    
                                    # Strategy 2: Use Roblox CDN direct URL (if available)
                                    # Some outfits have direct CDN URLs
                                    outfit["cdn_url"] = f"https://www.roblox.com/outfit-thumbnail/image?userOutfitId={outfit_id}&width=420&height=420&format=png"
                                    
                                    # Strategy 3: Use the outfit page thumbnail
                                    outfit["page_url"] = f"https://www.roblox.com/catalog/{outfit_id}"
                                    
                                    logger.info(f"[OUTFITS HARD TEST] Generated thumbnail URLs for user-created outfit '{outfit_name}' (ID: {outfit_id})")
                        
                        return user_created_outfits
            
            try:
                outfits = await _roblox_outfits_circuit_breaker.call(_fetch)
                logger.info(f"[OUTFITS HARD TEST] ✅ Retrieved {len(outfits)} user-created outfits (isEditable: True) for user {roblox_user_id}")
                if outfits:
                    logger.info(f"[OUTFITS HARD TEST] User-created outfit IDs: {[o.get('id') for o in outfits]}")
                    logger.info(f"[OUTFITS HARD TEST] User-created outfit names: {[o.get('name') for o in outfits[:10]]}")
                    logger.info(f"[OUTFITS HARD TEST] All outfits are user-created (isEditable: True) - filtered from total")
                else:
                    logger.info(f"[OUTFITS HARD TEST] No user-created outfits found for user {roblox_user_id}")
                return outfits
            except CircuitBreakerOpenError as e:
                logger.error(f"[OUTFITS HARD TEST] Circuit breaker is OPEN for user {roblox_user_id}: {e}")
                return []
            except Exception as e:
                logger.error(f"[OUTFITS HARD TEST] Error fetching outfits for user {roblox_user_id}: {e}", exc_info=True)
                return []
        
        except Exception as e:
            logger.error(f"[OUTFITS HARD TEST] Unexpected error getting outfits for user {roblox_user_id}: {e}", exc_info=True)
            return []
    
    def _generate_outfit_thumbnail_url(self, outfit_id: int) -> str:
        """
        Generate thumbnail URL for an outfit using the correct Roblox format.
        
        Args:
            outfit_id: Outfit ID
        
        Returns:
            Thumbnail URL string
        """
        # Correct format: https://www.roblox.com/outfit-thumbnail/image?userOutfitId={OutfitId}
        return f"https://www.roblox.com/outfit-thumbnail/image?userOutfitId={outfit_id}&width=420&height=420&format=png"
    
    async def get_outfit_details(self, outfit_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific outfit.
        
        Args:
            outfit_id: Outfit ID
        
        Returns:
            Dict with outfit details:
            - id: Outfit ID
            - name: Outfit name
            - isEditable: Whether outfit is editable
            - assets: List of equipped assets
            - bodyColors: Body color settings
            - scale: Avatar scale settings
        """
        try:
            url = f"{self.api_base}/outfits/{outfit_id}/details"
            
            async def _fetch():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 404:
                            logger.debug(f"Outfit {outfit_id} not found")
                            return None
                        
                        if response.status != 200:
                            logger.warning(f"Roblox Outfits API returned status {response.status} for outfit {outfit_id}")
                            return None
                        
                        return await response.json()
            
            try:
                details = await _roblox_outfits_circuit_breaker.call(_fetch)
                return details
            except CircuitBreakerOpenError as e:
                logger.error(f"[OUTFITS] Circuit breaker is OPEN for outfit {outfit_id}: {e}")
                return None
            except Exception as e:
                logger.error(f"[OUTFITS] Error fetching outfit details for {outfit_id}: {e}", exc_info=True)
                return None
        
        except Exception as e:
            logger.error(f"[OUTFITS] Unexpected error getting outfit details for {outfit_id}: {e}", exc_info=True)
            return None


# Singleton instance
_roblox_outfits_service: Optional[RobloxOutfitsService] = None


def get_roblox_outfits_service() -> RobloxOutfitsService:
    """Get singleton instance of RobloxOutfitsService"""
    global _roblox_outfits_service
    if _roblox_outfits_service is None:
        _roblox_outfits_service = RobloxOutfitsService()
    return _roblox_outfits_service

