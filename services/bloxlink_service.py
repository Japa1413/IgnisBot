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
from utils.retry import retry_with_backoff, CircuitBreaker, CircuitBreakerOpenError
import os

logger = get_logger(__name__)

# Circuit breaker for Bloxlink API
_bloxlink_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=aiohttp.ClientError
)


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
            
            # Use retry with circuit breaker
            async def _fetch():
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
                        return data
            
            try:
                data = await _bloxlink_circuit_breaker.call(_fetch)
            except CircuitBreakerOpenError as e:
                logger.error(f"Circuit breaker open for Bloxlink API: {e}")
                return None
            except Exception as e:
                # Retry with exponential backoff
                try:
                    data = await retry_with_backoff(
                        _fetch,
                        max_retries=3,
                        initial_delay=1.0,
                        max_delay=10.0
                    )
                except Exception as retry_error:
                    logger.error(f"All retries failed for Bloxlink API: {retry_error}")
                    return None
            
            if data is None:
                return None
            
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
    
    async def get_roblox_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Roblox user data by username (not display name).
        
        Uses multiple strategies to find the user:
        1. Primary: Username-to-userid endpoint (POST /v1/usernames/users) - most reliable
        2. Fallback: User search API (GET /v1/users/search) - if primary fails
        
        Args:
            username: Roblox username (not display name)
        
        Returns:
            Dict with:
            - username: Roblox username (actual username with correct casing)
            - id: Roblox user ID
            - avatar_url: Roblox avatar URL
            - verified: Always True (found by username)
            Or None if user not found
        """
        username = username.strip()
        if not username:
            logger.warning("Empty username provided")
            return None
        
        try:
            # Strategy 1: Use username-to-userid endpoint (most reliable)
            # This endpoint directly converts username to user data (returns ID, name, displayName, etc.)
            user_data = await self._get_user_by_username_direct(username)
            
            if user_data:
                found_username = user_data.get("name", "")  # Actual username (may have different casing)
                requested_username = user_data.get("requestedUsername", "")
                roblox_id = user_data.get("id")
                
                # Verify that the requested username matches (case-insensitive)
                # The API returns the actual username which may have different casing
                if roblox_id and requested_username.lower() == username.lower():
                    avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={roblox_id}&width=420&height=420&format=png"
                    
                    logger.info(f"Successfully found Roblox user: {found_username} (ID: {roblox_id}, requested: {requested_username})")
                    return {
                        "username": found_username,  # Use actual username from API (with correct casing)
                        "id": roblox_id,
                        "avatar_url": avatar_url,
                        "verified": True
                    }
                else:
                    logger.warning(f"Username mismatch: requested '{username}', got '{requested_username}'")
            
            # Strategy 2: Fallback to user search API
            logger.debug(f"Username-to-ID lookup failed, trying search API for '{username}'")
            user_data = await self._search_user_by_username(username)
            
            if user_data:
                found_username = user_data.get("name", "")
                roblox_id = user_data.get("id")
                
                # Verify exact match (case-insensitive)
                if found_username.lower() == username.lower() and roblox_id:
                    avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={roblox_id}&width=420&height=420&format=png"
                    
                    logger.info(f"Successfully found Roblox user via search: {found_username} (ID: {roblox_id})")
                    return {
                        "username": found_username,
                        "id": roblox_id,
                        "avatar_url": avatar_url,
                        "verified": True
                    }
            
            logger.warning(f"User '{username}' not found on Roblox using any method")
            return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching Roblox user by username '{username}': {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_roblox_user_by_username for '{username}': {e}", exc_info=True)
            return None
    
    async def _get_user_by_username_direct(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Roblox user data directly by username using the username-to-userid endpoint.
        
        This is the most reliable method as it directly converts username to user data.
        
        Args:
            username: Roblox username
        
        Returns:
            User data dict or None if not found
        """
        try:
            # Roblox API endpoint: POST /v1/usernames/users
            url = "https://users.roblox.com/v1/usernames/users"
            headers = {"Content-Type": "application/json"}
            payload = {"usernames": [username], "excludeBannedUsers": False}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        users = data.get("data", [])
                        if users and len(users) > 0:
                            user_data = users[0]
                            logger.debug(f"Found user data for username '{username}': {user_data.get('name')} (ID: {user_data.get('id')})")
                            return user_data
                    
                    logger.debug(f"Username-to-userid endpoint returned status {response.status} for '{username}'")
                    if response.status != 200:
                        try:
                            error_text = await response.text()
                            logger.debug(f"Error response: {error_text[:200]}")
                        except:
                            pass
                    return None
                    
        except Exception as e:
            logger.debug(f"Error in _get_user_by_username_direct for '{username}': {e}")
            return None
    
    async def _get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Roblox user data by user ID.
        
        Args:
            user_id: Roblox user ID
        
        Returns:
            User data dict or None if not found
        """
        try:
            url = f"https://users.roblox.com/v1/users/{user_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.debug(f"User details API returned status {response.status} for user ID {user_id}")
                        return None
        except Exception as e:
            logger.debug(f"Error in _get_user_by_id for user ID {user_id}: {e}")
            return None
    
    async def _search_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Search for Roblox user by username using search API (fallback method).
        
        Args:
            username: Roblox username
        
        Returns:
            User data dict or None if not found
        """
        try:
            url = "https://users.roblox.com/v1/users/search"
            # Note: limit must be one of: 10, 25, 50, 100
            params = {"keyword": username, "limit": 10}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        logger.debug(f"Search API returned status {response.status} for username '{username}'")
                        try:
                            error_text = await response.text()
                            logger.debug(f"Error response: {error_text[:200]}")
                        except:
                            pass
                        return None
                    
                    data = await response.json()
                    users = data.get("data", [])
                    
                    if not users:
                        logger.debug(f"No users found in search for '{username}'")
                        return None
                    
                    # Find exact match (case-insensitive)
                    for user in users:
                        found_username = user.get("name", "")
                        if found_username.lower() == username.lower():
                            logger.debug(f"Found exact match in search: '{found_username}'")
                            return user
                    
                    logger.debug(f"No exact match found in search results for '{username}'")
                    return None
                    
        except Exception as e:
            logger.debug(f"Error in _search_user_by_username for '{username}': {e}")
            return None

