"""
Event Announcement - Post formatted event announcements with Salamanders theme.
"""

from __future__ import annotations

import discord
from typing import Optional

# Role ID for Salamanders event pings
SALAMANDERS_ROLE_ID = 1376831480931815424


async def post_event_announcement(
    bot: discord.Client,
    channel_id: int,
    *,
    title: str,
    description: str,
    when: str,
    location: str,
    link: Optional[str] = None,
    color: int = 0x2B2D31,
    ping_role_id: Optional[int] = None,
    image_url: Optional[str] = None,
    footer_text: Optional[str] = None,
    footer_icon: Optional[str] = None,
    author_name: Optional[str] = None,
    author_icon: Optional[str] = None,
) -> None:
    """
    Post a formatted event announcement embed into a specific channel.
    
    Styled for Salamanders Chapter of Warhammer 40,000.

    Parameters
    ----------
    bot : discord.Client
        The running bot/client instance.
    channel_id : int
        Target text channel ID where the announcement will be posted.
    title : str
        Embed title.
    description : str
        Main description/body of the announcement.
    when : str
        Human-readable date/time (e.g., 'Tonight at 20:00 (server time)').
    location : str
        Where it happens (e.g., 'Main Discord VC', 'Training Grounds').
    link : Optional[str]
        Optional URL with more info.
    color : int
        Embed color (default Salamanders green/orange).
    ping_role_id : Optional[int]
        If provided, will @mention this role above the embed.
        Defaults to SALAMANDERS_ROLE_ID if None.
    image_url : Optional[str]
        Optional image to display in the embed (banner).
    footer_text : Optional[str]
        Optional footer text.
    footer_icon : Optional[str]
        Optional footer icon URL.
    author_name : Optional[str]
        Optional author text at top-left of the embed.
    author_icon : Optional[str]
        Optional author icon URL.

    Raises
    ------
    RuntimeError
        If channel is not found or not a text-capable channel.
    """
    channel = bot.get_channel(channel_id)
    if channel is None:
        raise RuntimeError(f"Channel {channel_id} not found or bot has no access.")

    if not hasattr(channel, "send"):
        raise RuntimeError(f"Channel {channel_id} is not a text-capable channel.")

    embed = discord.Embed(title=title, description=description, color=color)

    # Author (optional)
    if author_name:
        embed.set_author(name=author_name, icon_url=author_icon or discord.Embed.Empty)

    # Core fields
    embed.add_field(name="📅 When", value=when, inline=False)
    embed.add_field(name="📍 Location", value=location, inline=False)

    # Link (optional)
    if link:
        embed.add_field(name="🔗 Link", value=link, inline=False)

    # Image (optional)
    if image_url:
        embed.set_image(url=image_url)

    # Footer (optional)
    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon or discord.Embed.Empty)

    # Optional role ping (default to Salamanders role if not specified)
    content = None
    role_id_to_use = ping_role_id if ping_role_id is not None else SALAMANDERS_ROLE_ID
    
    if role_id_to_use:
        if isinstance(channel, (discord.TextChannel, discord.Thread)):
            role = channel.guild.get_role(role_id_to_use)
            if role:
                content = role.mention

    await channel.send(content=content, embed=embed)
