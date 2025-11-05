"""
Bloxlink Service - Integration with Bloxlink API for Roblox data.

This service handles all interactions with Bloxlink to retrieve:
- Roblox username (not display name)
- Roblox user ID
- Roblox avatar URL
- Verification status
"""

from __future__ import annotations

import aiohttp
from typing import Optional, Dict, Any
from utils.logger import get_logger
import os

logger = get_logger(__name__)


class BloxlinkService:
    """Service for Bloxlink API integration"""
    
    def __init__(self):
        """Initialize Bloxlink service"""
        # Bloxlink API base URL
        self.api_base = "https://api.blox.link/v4"
        # Get API key from environment if available
        self.api_key = os.getenv("BLOXLINK_API_KEY", "")
    
    async def get_roblox_user(
        self,
        discord_id: int,
        guild_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get Roblox user data from Bloxlink API.
        
        Args:
            discord_id: Discord user ID
            guild_id: Discord guild ID (optional, for guild-specific verification)
        
        Returns:
            Dict with:
            - username: Roblox username (not display name)
            - id: Roblox user ID
            - avatar_url: Roblox avatar URL
            - verified: Boolean indicating verification status
            - verified_at: Timestamp of verification (if available)
            Or None if user not found or not verified
        """
        try:
            # Build API URL
            url = f"{self.api_base}/public/guilds/{guild_id}/discord-to-roblox/{discord_id}"
            if not guild_id:
                # Fallback to global lookup
                url = f"{self.api_base}/public/discord-to-roblox/{discord_id}"
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 404:
                        # User not found or not verified
                        logger.debug(f"User {discord_id} not found in Bloxlink")
                        return None
                    
                    if response.status != 200:
                        logger.warning(f"Bloxlink API returned status {response.status} for user {discord_id}")
                        return None
                    
                    data = await response.json()
                    
                    # Bloxlink API response structure
                    roblox_user_id = data.get("robloxId")
                    if not roblox_user_id:
                        logger.debug(f"User {discord_id} has no Roblox ID in Bloxlink")
                        return None
                    
                    # Get username from Roblox API
                    username = await self._get_roblox_username(roblox_user_id)
                    
                    # Build avatar URL
                    avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={roblox_user_id}&width=420&height=420&format=png"
                    
                    return {
                        "username": username or f"User_{roblox_user_id}",
                        "id": roblox_user_id,
                        "avatar_url": avatar_url,
                        "verified": True,
                        "verified_at": data.get("verifiedAt")
                    }
                    
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching Bloxlink data for user {discord_id}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_roblox_user for {discord_id}: {e}", exc_info=True)
            return None
    
    async def _get_roblox_username(self, roblox_id: int) -> Optional[str]:
        """
        Get Roblox username from Roblox API.
        This ensures we get the actual username, not the display name.
        
        Args:
            roblox_id: Roblox user ID
        
        Returns:
            Username string or None
        """
        try:
            url = f"https://users.roblox.com/v1/users/{roblox_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Get username (not displayName)
                        return data.get("name")
                    else:
                        logger.warning(f"Roblox API returned status {response.status} for user {roblox_id}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching Roblox username for {roblox_id}: {e}", exc_info=True)
            return None
    
    async def is_verified(
        self,
        discord_id: int,
        guild_id: Optional[int] = None
    ) -> bool:
        """
        Check if user is verified with Bloxlink.
        
        Args:
            discord_id: Discord user ID
            guild_id: Discord guild ID (optional)
        
        Returns:
            True if verified, False otherwise
        """
        user_data = await self.get_roblox_user(discord_id, guild_id)
        return user_data is not None and user_data.get("verified", False)
    
    async def get_user_avatar_url(self, roblox_id: int) -> str:
        """
        Get Roblox avatar URL for a user.
        
        Args:
            roblox_id: Roblox user ID
        
        Returns:
            Avatar URL string
        """
        return f"https://www.roblox.com/headshot-thumbnail/image?userId={roblox_id}&width=420&height=420&format=png"

