"""
Interaction Helpers - Utilities for handling Discord interactions with timeout protection.
"""

from __future__ import annotations

import asyncio
import discord
from typing import Optional, Callable, Awaitable
from utils.logger import get_logger

logger = get_logger(__name__)

# Discord interaction timeout is 3 seconds
INTERACTION_TIMEOUT = 3.0


async def safe_interaction_response(
    interaction: discord.Interaction,
    response_func: Callable[[], Awaitable],
    timeout: float = INTERACTION_TIMEOUT,
    retry_count: int = 1
) -> bool:
    """
    Safely handle interaction response with timeout protection and retry logic.
    
    Args:
        interaction: Discord interaction object
        response_func: Async function that sends the response
        timeout: Maximum time to wait for response (default: 3 seconds)
        retry_count: Number of retry attempts (default: 1)
    
    Returns:
        True if response was sent successfully, False otherwise
    """
    for attempt in range(retry_count + 1):
        try:
            # Check if interaction is still valid
            if interaction.response.is_done():
                logger.warning(f"Interaction {interaction.id} already responded (attempt {attempt + 1})")
                return False
            
            # Try to send response with timeout
            await asyncio.wait_for(response_func(), timeout=timeout)
            return True
            
        except asyncio.TimeoutError:
            logger.warning(f"Interaction {interaction.id} timed out (attempt {attempt + 1}/{retry_count + 1})")
            if attempt < retry_count:
                await asyncio.sleep(0.5)  # Small delay before retry
                continue
            return False
            
        except discord.errors.InteractionResponded:
            logger.debug(f"Interaction {interaction.id} already responded")
            return True
            
        except discord.errors.NotFound:
            logger.warning(f"Interaction {interaction.id} not found (may have expired)")
            return False
            
        except Exception as e:
            logger.error(f"Error responding to interaction {interaction.id}: {e}", exc_info=True)
            if attempt < retry_count:
                await asyncio.sleep(0.5)
                continue
            return False
    
    return False


async def safe_followup_send(
    interaction: discord.Interaction,
    *args,
    timeout: float = 5.0,
    **kwargs
) -> Optional[discord.WebhookMessage]:
    """
    Safely send followup message with timeout protection.
    
    Args:
        interaction: Discord interaction object
        *args: Arguments to pass to followup.send()
        timeout: Maximum time to wait (default: 5 seconds)
        **kwargs: Keyword arguments to pass to followup.send()
    
    Returns:
        WebhookMessage if sent successfully, None otherwise
    """
    try:
        return await asyncio.wait_for(
            interaction.followup.send(*args, **kwargs),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.warning(f"Followup send timed out for interaction {interaction.id}")
        return None
    except discord.errors.NotFound:
        logger.warning(f"Interaction {interaction.id} not found for followup")
        return None
    except Exception as e:
        logger.error(f"Error sending followup for interaction {interaction.id}: {e}", exc_info=True)
        return None


def get_channel_help_message(command_name: str, allowed_channel_ids: list[int], bot: discord.Client) -> str:
    """
    Generate a helpful error message for channel restrictions.
    
    Args:
        command_name: Name of the command
        allowed_channel_ids: List of allowed channel IDs
        bot: Discord bot client to fetch channel names
    
    Returns:
        Formatted help message
    """
    if not allowed_channel_ids:
        return f"❌ The `/{command_name}` command has channel restrictions, but no allowed channels are configured."
    
    # Try to get channel names
    channel_names = []
    for channel_id in allowed_channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            channel_names.append(f"**#{channel.name}**")
        else:
            channel_names.append(f"channel with ID `{channel_id}`")
    
    channels_text = ", ".join(channel_names) if len(channel_names) > 1 else channel_names[0]
    
    return (
        f"❌ The `/{command_name}` command can only be used in {channels_text}.\n\n"
        f"💡 **Tip:** Navigate to the correct channel and try again.\n"
        f"📖 For more information, use `/help` or check the documentation."
    )

