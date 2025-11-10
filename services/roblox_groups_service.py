"""
Roblox Groups Service - Integration with Roblox Groups API.

This service handles all interactions with Roblox Groups API to retrieve:
- Group membership information
- User rank in groups
- Group details
"""

from __future__ import annotations

import os
import aiohttp
from typing import Optional, Dict, Any, List
from utils.logger import get_logger
from utils.retry import retry_with_backoff, CircuitBreaker, CircuitBreakerOpenError

logger = get_logger(__name__)

# Circuit breaker for Roblox Groups API
_roblox_groups_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=aiohttp.ClientError
)

# Age of Warfare Group IDs (configurable via environment variable)
# Can be comma-separated list: "6302485,35732475,35718467,6496437,6340169,36088185"
AOW_GROUP_IDS_STR = os.getenv("AOW_GROUP_IDS", "6302485,35732475,35718467,6496437,6340169,36088185")
AOW_GROUP_IDS = [int(gid.strip()) for gid in AOW_GROUP_IDS_STR.split(",") if gid.strip().isdigit()]

# Legacy support for single group ID
AOW_GROUP_ID = int(os.getenv("AOW_GROUP_ID", "0"))  # Set via environment variable or config


class RobloxGroupsService:
    """Service for Roblox Groups API integration"""
    
    def __init__(self):
        """Initialize Roblox Groups service"""
        # Roblox API base URL
        self.api_base = "https://groups.roblox.com/v1"
        # Roblox API for user groups
        self.users_api_base = "https://users.roblox.com/v1"
    
    async def get_user_groups(self, roblox_user_id: int) -> List[Dict[str, Any]]:
        """
        Get all groups a user is a member of.
        
        Args:
            roblox_user_id: Roblox user ID
        
        Returns:
            List of groups with:
            - id: Group ID
            - name: Group name
            - memberCount: Number of members
            - rank: User's rank in the group
            - role: User's role name in the group
        """
        try:
            url = f"{self.api_base}/users/{roblox_user_id}/groups/roles"
            
            async def _fetch():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 404:
                            logger.debug(f"User {roblox_user_id} not found or has no groups")
                            return []
                        
                        if response.status != 200:
                            logger.warning(f"Roblox Groups API returned status {response.status} for user {roblox_user_id}")
                            return []
                        
                        data = await response.json()
                        return data.get("data", [])
            
            try:
                groups_data = await _roblox_groups_circuit_breaker.call(_fetch)
            except CircuitBreakerOpenError as e:
                logger.error(f"Circuit breaker open for Roblox Groups API: {e}")
                return []
            except Exception as e:
                # Retry with exponential backoff
                try:
                    groups_data = await retry_with_backoff(
                        _fetch,
                        max_retries=3,
                        initial_delay=1.0,
                        max_delay=10.0
                    )
                except Exception as retry_error:
                    logger.error(f"Error fetching user groups after retries: {retry_error}", exc_info=True)
                    return []
            
            if not groups_data:
                return []
            
            # Format groups data
            groups = []
            for group_data in groups_data:
                group_info = group_data.get("group", {})
                role_info = group_data.get("role", {})
                
                groups.append({
                    "id": group_info.get("id"),
                    "name": group_info.get("name"),
                    "memberCount": group_info.get("memberCount", 0),
                    "rank": role_info.get("rank", 0),
                    "role": role_info.get("name", "Unknown"),
                    "roleId": role_info.get("id")
                })
            
            # Sort by rank (highest first)
            groups.sort(key=lambda x: x.get("rank", 0), reverse=True)
            
            return groups
            
        except Exception as e:
            logger.error(f"Error getting user groups for {roblox_user_id}: {e}", exc_info=True)
            return []
    
    async def get_user_rank_in_group(self, roblox_user_id: int, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user's rank in a specific group.
        
        Args:
            roblox_user_id: Roblox user ID
            group_id: Group ID
        
        Returns:
            Dict with:
            - rank: User's rank number
            - role: User's role name
            - roleId: Role ID
            Or None if user is not in the group
        """
        try:
            # Get all user groups and find the specific one
            groups = await self.get_user_groups(roblox_user_id)
            
            for group in groups:
                if group.get("id") == group_id:
                    return {
                        "rank": group.get("rank"),
                        "role": group.get("role"),
                        "roleId": group.get("roleId")
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user rank in group {group_id} for user {roblox_user_id}: {e}", exc_info=True)
            return None
    
    async def is_user_in_group(self, roblox_user_id: int, group_id: int) -> bool:
        """
        Check if user is a member of a specific group.
        
        Args:
            roblox_user_id: Roblox user ID
            group_id: Group ID
        
        Returns:
            True if user is in the group, False otherwise
        """
        rank_info = await self.get_user_rank_in_group(roblox_user_id, group_id)
        return rank_info is not None
    
    async def get_group_info(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a group.
        
        Args:
            group_id: Group ID
        
        Returns:
            Dict with group information:
            - id: Group ID
            - name: Group name
            - description: Group description
            - memberCount: Number of members
            - owner: Group owner info
        """
        try:
            url = f"{self.api_base}/groups/{group_id}"
            
            async def _fetch():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 404:
                            logger.debug(f"Group {group_id} not found")
                            return None
                        
                        if response.status != 200:
                            logger.warning(f"Roblox Groups API returned status {response.status} for group {group_id}")
                            return None
                        
                        return await response.json()
            
            try:
                group_data = await _roblox_groups_circuit_breaker.call(_fetch)
            except CircuitBreakerOpenError as e:
                logger.error(f"Circuit breaker open for Roblox Groups API: {e}")
                return None
            except Exception as e:
                try:
                    group_data = await retry_with_backoff(
                        _fetch,
                        max_retries=3,
                        initial_delay=1.0,
                        max_delay=10.0
                    )
                except Exception as retry_error:
                    logger.error(f"Error fetching group info after retries: {retry_error}", exc_info=True)
                    return None
            
            return group_data
            
        except Exception as e:
            logger.error(f"Error getting group info for {group_id}: {e}", exc_info=True)
            return None
    
    async def check_user_in_groups(
        self, 
        roblox_user_id: int, 
        group_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Check if user is in multiple groups and return their rank info.
        
        Args:
            roblox_user_id: Roblox user ID
            group_ids: List of group IDs to check
        
        Returns:
            List of groups where user is found, with:
            - id: Group ID
            - name: Group name
            - rank: User's rank number
            - role: User's role name
        """
        found_groups = []
        
        # Get all user groups first (more efficient)
        user_groups = await self.get_user_groups(roblox_user_id)
        user_group_ids = {group.get("id"): group for group in user_groups}
        
        # Check each requested group
        for group_id in group_ids:
            if group_id in user_group_ids:
                # User is in this group, get full info
                group_data = user_group_ids[group_id]
                
                # Get group name from API
                group_info = await self.get_group_info(group_id)
                group_name = group_info.get("name", "Unknown Group") if group_info else group_data.get("name", "Unknown Group")
                
                found_groups.append({
                    "id": group_id,
                    "name": group_name,
                    "rank": group_data.get("rank", 0),
                    "role": group_data.get("role", "Unknown")
                })
        
        return found_groups
    
    async def check_pending_request(
        self,
        group_id: int,
        roblox_user_id: int,
        roblox_cookie: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if user has a pending join request for a group.
        
        Args:
            group_id: Group ID
            roblox_user_id: Roblox user ID
            roblox_cookie: Roblox authentication cookie (required)
        
        Returns:
            Dict with:
            - has_request: bool
            - message: str
        """
        if not roblox_cookie:
            return {
                "has_request": False,
                "message": "Roblox cookie is required"
            }
        
        try:
            # Check pending requests for the group
            url = f"{self.api_base}/groups/{group_id}/join-requests"
            
            headers = {
                "Cookie": f".ROBLOSECURITY={roblox_cookie}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        requests = data.get("data", [])
                        
                        # Log for debugging
                        logger.info(f"[CHECK_REQUEST] Found {len(requests)} pending requests for group {group_id}")
                        logger.info(f"[CHECK_REQUEST] Looking for user ID: {roblox_user_id}")
                        
                        # Check if user ID is in the requests
                        # The structure might be: requester.userId or just userId
                        for req in requests:
                            requester = req.get("requester", {})
                            req_user_id = requester.get("userId") if requester else req.get("userId")
                            
                            # Log each request for debugging
                            logger.debug(f"[CHECK_REQUEST] Checking request: user_id={req_user_id}, full_req={req}")
                            
                            if req_user_id == roblox_user_id:
                                logger.info(f"[CHECK_REQUEST] Found pending request for user {roblox_user_id}")
                                return {
                                    "has_request": True,
                                    "message": "User has a pending join request"
                                }
                        
                        logger.warning(f"[CHECK_REQUEST] No pending request found for user {roblox_user_id} in {len(requests)} requests")
                        return {
                            "has_request": False,
                            "message": "User does not have a pending join request"
                        }
                    elif response.status == 403:
                        # Might need CSRF token or no permission
                        return {
                            "has_request": False,
                            "message": "Could not check requests (no permission or authentication required)"
                        }
                    else:
                        error_text = await response.text()
                        logger.warning(f"[CHECK_REQUEST] API returned status {response.status}: {error_text[:200]}")
                        return {
                            "has_request": False,
                            "message": f"Could not check requests (status {response.status})"
                        }
        except Exception as e:
            logger.error(f"Error checking pending request: {e}", exc_info=True)
            return {
                "has_request": False,
                "message": f"Error checking request: {str(e)}"
            }
    
    async def accept_user_to_group(
        self,
        group_id: int,
        roblox_user_id: int,
        roblox_cookie: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Accept a user's join request to a group.
        
        Args:
            group_id: Group ID
            roblox_user_id: Roblox user ID to accept
            roblox_cookie: Roblox authentication cookie (required for this operation)
        
        Returns:
            Dict with:
            - success: bool
            - message: str
            - error: Optional[str]
        """
        if not roblox_cookie:
            return {
                "success": False,
                "message": "Roblox cookie is required for accepting members",
                "error": "Missing authentication"
            }
        
        try:
            # Accept user's join request to the group
            # Correct endpoint: POST /v1/groups/{groupId}/join-requests/users/{userId}
            url = f"{self.api_base}/groups/{group_id}/join-requests/users/{roblox_user_id}"
            
            headers = {
                "Cookie": f".ROBLOSECURITY={roblox_cookie}",
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": ""  # Will be fetched if needed
            }
            
            async def _accept():
                async with aiohttp.ClientSession() as session:
                    # Get CSRF token first by making a POST request to any endpoint
                    # Roblox requires a POST request to get CSRF token
                    try:
                        # Make a dummy POST request to get CSRF token
                        csrf_url = f"{self.api_base}/groups/{group_id}"
                        async with session.post(csrf_url, headers={"Cookie": f".ROBLOSECURITY={roblox_cookie}"}, timeout=aiohttp.ClientTimeout(total=10)) as csrf_response:
                            csrf_token = csrf_response.headers.get("X-CSRF-TOKEN")
                            if csrf_token:
                                headers["X-CSRF-TOKEN"] = csrf_token
                                logger.info(f"[ACCEPT] Got CSRF token: {csrf_token[:20]}...")
                            else:
                                logger.warning(f"[ACCEPT] No CSRF token in response headers")
                    except Exception as e:
                        logger.warning(f"[ACCEPT] Could not get CSRF token: {e}")
                    
                    # Now try to accept with the correct endpoint
                    async with session.post(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        response_text = await response.text()
                        logger.info(f"[ACCEPT] Response status: {response.status}, URL: {url}")
                        logger.debug(f"[ACCEPT] Response body: {response_text[:300]}")
                        logger.debug(f"[ACCEPT] Response headers: {dict(response.headers)}")
                        
                        if response.status == 403:
                            # Need CSRF token - try to get it from response
                            csrf_token = response.headers.get("X-CSRF-TOKEN")
                            if csrf_token:
                                headers["X-CSRF-TOKEN"] = csrf_token
                                logger.info(f"[ACCEPT] Got CSRF token from 403 response: {csrf_token[:20]}..., retrying...")
                                # Retry with CSRF token
                                async with session.post(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as retry_response:
                                    retry_text = await retry_response.text()
                                    logger.info(f"[ACCEPT] Retry response status: {retry_response.status}")
                                    logger.debug(f"[ACCEPT] Retry response body: {retry_text[:300]}")
                                    if retry_response.status == 200:
                                        return {"success": True, "message": "User accepted to group"}
                                    elif retry_response.status == 403:
                                        # Still 403 after CSRF token - likely permission issue
                                        return {"success": False, "message": "Insufficient permissions to accept members. The Roblox account used does not have permission to accept join requests in this group.", "error": "Permission denied (403)"}
                                    else:
                                        return {"success": False, "message": f"Failed to accept user (status {retry_response.status})", "error": retry_text[:200]}
                            else:
                                # 403 without CSRF token in response - likely permission issue
                                return {"success": False, "message": "Insufficient permissions to accept members. The Roblox account used does not have permission to accept join requests in this group. Please ensure the account has admin permissions.", "error": "Permission denied (403 - no CSRF token)"}
                        
                        if response.status == 200:
                            return {"success": True, "message": "User accepted to group"}
                        elif response.status == 400:
                            # User might already be in group or no pending request
                            if "already" in response_text.lower() or "member" in response_text.lower():
                                return {"success": True, "message": "User is already a member of the group"}
                            # Check if it's a "no pending request" error
                            if "request" in response_text.lower() or "pending" in response_text.lower() or "not found" in response_text.lower():
                                return {"success": False, "message": "User does not have a pending join request. Please ask the user to request to join the group first.", "error": "No pending request (400)"}
                            return {"success": False, "message": "Invalid request", "error": response_text[:200]}
                        elif response.status == 404:
                            # 404 might mean wrong endpoint - try alternative format
                            logger.warning(f"[ACCEPT] 404 with endpoint {url}, trying alternative...")
                            alt_url = f"{self.api_base}/groups/{group_id}/requests/{roblox_user_id}/accept"
                            logger.info(f"[ACCEPT] Trying alternative: {alt_url}")
                            async with session.post(alt_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as alt_response:
                                alt_text = await alt_response.text()
                                logger.info(f"[ACCEPT] Alternative response: {alt_response.status}")
                                if alt_response.status == 200:
                                    return {"success": True, "message": "User accepted to group"}
                                elif alt_response.status == 403:
                                    alt_csrf = alt_response.headers.get("X-CSRF-TOKEN")
                                    if alt_csrf:
                                        headers["X-CSRF-TOKEN"] = alt_csrf
                                        async with session.post(alt_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as alt_retry:
                                            if alt_retry.status == 200:
                                                return {"success": True, "message": "User accepted to group"}
                            # If both endpoints fail with 404, assume no request
                            return {"success": False, "message": "User does not have a pending join request for this group. Please ask the user to request to join the group (ID: {}) first.".format(group_id), "error": "No pending request (404)"}
                        elif response.status == 401 or response.status == 403:
                            return {"success": False, "message": "Authentication failed or insufficient permissions", "error": f"Invalid or expired cookie (status {response.status})"}
                        else:
                            return {"success": False, "message": f"API returned status {response.status}", "error": response_text[:200]}
            
            result = await _accept()
            return result
            
        except Exception as e:
            logger.error(f"Error accepting user {roblox_user_id} to group {group_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error accepting user: {str(e)}",
                "error": str(e)
            }
    
    async def set_user_rank(
        self,
        group_id: int,
        roblox_user_id: int,
        role_id: int,
        roblox_cookie: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Set a user's rank in a group.
        
        Args:
            group_id: Group ID
            roblox_user_id: Roblox user ID
            role_id: Role ID to set (rank ID)
            roblox_cookie: Roblox authentication cookie (required)
        
        Returns:
            Dict with:
            - success: bool
            - message: str
            - error: Optional[str]
        """
        if not roblox_cookie:
            return {
                "success": False,
                "message": "Roblox cookie is required for setting ranks",
                "error": "Missing authentication"
            }
        
        try:
            url = f"{self.api_base}/groups/{group_id}/users/{roblox_user_id}"
            
            headers = {
                "Cookie": f".ROBLOSECURITY={roblox_cookie}",
                "Content-Type": "application/json",
                "X-CSRF-TOKEN": ""
            }
            
            payload = {
                "roleId": role_id
            }
            
            async def _set_rank():
                async with aiohttp.ClientSession() as session:
                    # First request to get CSRF token
                    async with session.patch(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 403:
                            # Need CSRF token
                            csrf_token = response.headers.get("X-CSRF-TOKEN")
                            if csrf_token:
                                headers["X-CSRF-TOKEN"] = csrf_token
                                # Retry with CSRF token
                                async with session.patch(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as retry_response:
                                    if retry_response.status == 200:
                                        return {"success": True, "message": "User rank updated successfully"}
                                    else:
                                        error_text = await retry_response.text()
                                        return {"success": False, "message": f"Failed to set rank", "error": error_text[:200]}
                            else:
                                return {"success": False, "message": "CSRF token not available", "error": "Authentication failed"}
                        
                        if response.status == 200:
                            return {"success": True, "message": "User rank updated successfully"}
                        elif response.status == 400:
                            error_text = await response.text()
                            return {"success": False, "message": "Invalid request", "error": error_text[:200]}
                        elif response.status == 401 or response.status == 403:
                            return {"success": False, "message": "Authentication failed or insufficient permissions", "error": "Invalid cookie or no permission"}
                        else:
                            error_text = await response.text()
                            return {"success": False, "message": f"API returned status {response.status}", "error": error_text[:200]}
            
            result = await _set_rank()
            return result
            
        except Exception as e:
            logger.error(f"Error setting rank for user {roblox_user_id} in group {group_id}: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error setting rank: {str(e)}",
                "error": str(e)
            }
    
    async def get_group_roles(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Get all roles (ranks) in a group.
        
        Args:
            group_id: Group ID
        
        Returns:
            List of roles with:
            - id: Role ID
            - name: Role name
            - rank: Rank number
        """
        try:
            url = f"{self.api_base}/groups/{group_id}/roles"
            
            async def _fetch():
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status != 200:
                            logger.warning(f"Roblox Groups API returned status {response.status} for group {group_id} roles")
                            return []
                        
                        data = await response.json()
                        return data.get("roles", [])
            
            try:
                roles_data = await _roblox_groups_circuit_breaker.call(_fetch)
            except CircuitBreakerOpenError as e:
                logger.error(f"Circuit breaker open for Roblox Groups API: {e}")
                return []
            except Exception as e:
                try:
                    roles_data = await retry_with_backoff(
                        _fetch,
                        max_retries=3,
                        initial_delay=1.0,
                        max_delay=10.0
                    )
                except Exception as retry_error:
                    logger.error(f"Error fetching group roles after retries: {retry_error}", exc_info=True)
                    return []
            
            # Format roles data
            roles = []
            for role_data in roles_data:
                roles.append({
                    "id": role_data.get("id"),
                    "name": role_data.get("name"),
                    "rank": role_data.get("rank", 0)
                })
            
            # Sort by rank (lowest first)
            roles.sort(key=lambda x: x.get("rank", 0))
            
            return roles
            
        except Exception as e:
            logger.error(f"Error getting group roles for {group_id}: {e}", exc_info=True)
            return []


# Singleton instance
_roblox_groups_service: Optional[RobloxGroupsService] = None


def get_roblox_groups_service() -> RobloxGroupsService:
    """Get singleton RobloxGroupsService instance"""
    global _roblox_groups_service
    if _roblox_groups_service is None:
        _roblox_groups_service = RobloxGroupsService()
    return _roblox_groups_service

