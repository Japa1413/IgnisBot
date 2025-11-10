"""
Bloxlink Integration Service - Integration with Bloxlink API for role updates.

This service handles sending rank and company information to Bloxlink
when /verify or /update commands are used, allowing Bloxlink to assign
the correct roles based on the user's Roblox rank.
"""

from __future__ import annotations

import aiohttp
from typing import Optional, Dict, Any
from utils.logger import get_logger
from utils.config import GUILD_ID
import os

logger = get_logger(__name__)

# Bloxlink API configuration
BLOXLINK_API_KEY = os.getenv("BLOXLINK_API_KEY", "")
BLOXLINK_API_BASE = "https://api.blox.link/v4"


class BloxlinkIntegrationService:
    """
    Service for integrating with Bloxlink API to send rank and company information.
    
    This allows Bloxlink to assign roles based on Roblox rank and company information.
    """
    
    def __init__(self):
        """Initialize Bloxlink Integration service"""
        self.api_base = BLOXLINK_API_BASE
        self.api_key = BLOXLINK_API_KEY
        self.guild_id = GUILD_ID
    
    async def send_user_update(
        self,
        discord_id: int,
        roblox_id: int,
        roblox_username: str,
        roblox_rank: Optional[str] = None,
        roblox_rank_number: Optional[int] = None,
        company_number: Optional[int] = None,
        group_id: int = 6340169
    ) -> Dict[str, Any]:
        """
        Send user update information to Bloxlink.
        
        This notifies Bloxlink about the user's current rank and company,
        allowing it to assign the correct Discord roles.
        
        Args:
            discord_id: Discord user ID
            roblox_id: Roblox user ID
            roblox_username: Roblox username
            roblox_rank: Roblox rank name (role name)
            roblox_rank_number: Roblox rank number
            company_number: Company number for this user
            group_id: Roblox group ID (default: 6340169)
        
        Returns:
            Dict with success status and message
        """
        try:
            if not self.api_key:
                logger.debug("Bloxlink API key not configured, skipping update notification")
                return {
                    "success": False,
                    "message": "Bloxlink API key not configured"
                }
            
            # Prepare data
            payload = {
                "discord_id": discord_id,
                "roblox_id": roblox_id,
                "roblox_username": roblox_username,
                "group_id": group_id,
            }
            
            if roblox_rank:
                payload["roblox_rank"] = roblox_rank
            if roblox_rank_number:
                payload["roblox_rank_number"] = roblox_rank_number
            if company_number:
                payload["company_number"] = company_number
            
            # Send update to Bloxlink
            url = f"{self.api_base}/public/guilds/{self.guild_id}/update-user"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"User update sent to Bloxlink for {discord_id} "
                            f"(Roblox: {roblox_username}, Rank: {roblox_rank})"
                        )
                        return {
                            "success": True,
                            "message": "Update sent to Bloxlink",
                            "data": data
                        }
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"Bloxlink API returned status {response.status}: {error_text[:200]}"
                        )
                        return {
                            "success": False,
                            "message": f"Bloxlink API error: {response.status}",
                            "error": error_text[:200]
                        }
        
        except Exception as e:
            logger.error(f"Error sending update to Bloxlink: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    async def trigger_bloxlink_update(
        self,
        discord_id: int,
        roblox_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Trigger Bloxlink to update a user's roles.
        
        This is a simpler method that just triggers Bloxlink's update process.
        
        Args:
            discord_id: Discord user ID
            roblox_id: Optional Roblox user ID (if not provided, Bloxlink will look it up)
        
        Returns:
            Dict with success status and message
        """
        try:
            if not self.api_key:
                logger.debug("Bloxlink API key not configured, skipping trigger")
                return {
                    "success": False,
                    "message": "Bloxlink API key not configured"
                }
            
            # Trigger update
            url = f"{self.api_base}/public/guilds/{self.guild_id}/update-user/{discord_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {}
            if roblox_id:
                payload["roblox_id"] = roblox_id
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload if payload else None,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Bloxlink update triggered for {discord_id}")
                        return {
                            "success": True,
                            "message": "Bloxlink update triggered",
                            "data": data
                        }
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"Bloxlink API returned status {response.status}: {error_text[:200]}"
                        )
                        return {
                            "success": False,
                            "message": f"Bloxlink API error: {response.status}",
                            "error": error_text[:200]
                        }
        
        except Exception as e:
            logger.error(f"Error triggering Bloxlink update: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }


# Singleton instance
_bloxlink_integration_service: Optional[BloxlinkIntegrationService] = None


def get_bloxlink_integration_service() -> BloxlinkIntegrationService:
    """Get singleton BloxlinkIntegrationService instance"""
    global _bloxlink_integration_service
    if _bloxlink_integration_service is None:
        _bloxlink_integration_service = BloxlinkIntegrationService()
    return _bloxlink_integration_service


