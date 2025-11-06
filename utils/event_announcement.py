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

    # Build description with Host, Description (if provided), and Link
    # No emojis, clean format
    description_parts = []
    
    # Host is always included (using author_name if provided)
    if author_name:
        description_parts.append(f"**Host:** {author_name}")
    
    # Description only if provided and not empty
    if description and description.strip():
        description_parts.append(f"**Description:** {description}")
    
    # Link is always included (use default if not provided)
    default_link = "https://www.roblox.com/games/99813489644549/Averium-Invicta-The-Grave-World"
    final_link = link if link else default_link
    description_parts.append(f"**Link:** {final_link}")
    
    embed = discord.Embed(
        title=title,
        description="\n".join(description_parts),
        color=color
    )

    # No image in embed (removed as requested)
    # Image removed: if image_url: embed.set_image(url=image_url)
    
    # Footer with specified icon
    footer_icon_url = "https://wa-cdn.nyc3.digitaloceanspaces.com/user-data/production/970c868b-efa5-4aa1-a4c6-8385fcc8e8f9/uploads/images/f77af3977263219d0bb678d720da6e6c.png"
    
    if footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_icon_url)
    else:
        embed.set_footer(icon_url=footer_icon_url)

    # Always ping Salamanders role (ID: 1376831480931815424)
    content = None
    if isinstance(channel, (discord.TextChannel, discord.Thread)):
        salamanders_role_id = 1376831480931815424
        role = channel.guild.get_role(salamanders_role_id)
        if role:
            content = role.mention
        else:
            # Fallback to preset role if specified
            role_id_to_use = ping_role_id if ping_role_id is not None else SALAMANDERS_ROLE_ID
            if role_id_to_use:
                role = channel.guild.get_role(role_id_to_use)
                if role:
                    content = role.mention

    await channel.send(content=content, embed=embed)
