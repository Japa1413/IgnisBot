"""
Autocomplete utilities for Discord slash commands.
"""

from __future__ import annotations

from typing import List, Optional
import discord
from discord import app_commands
from utils.logger import get_logger

logger = get_logger(__name__)


async def autocomplete_members(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    """
    Autocomplete for member mentions.
    
    Args:
        interaction: Discord interaction
        current: Current input text
    
    Returns:
        List of member choices
    """
    if not interaction.guild:
        return []
    
    # Get members matching current input
    members = interaction.guild.members
    matching = []
    
    current_lower = current.lower()
    for member in members[:25]:  # Limit to 25 results
        if current_lower in member.display_name.lower() or current_lower in member.name.lower():
            matching.append(
                app_commands.Choice(
                    name=f"{member.display_name} ({member.name})",
                    value=str(member.id)
                )
            )
    
    return matching[:25]  # Discord limit is 25 choices


async def autocomplete_ranks(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    """
    Autocomplete for rank names.
    
    Args:
        interaction: Discord interaction
        current: Current input text
    
    Returns:
        List of rank choices
    """
    # Common ranks (you can expand this list)
    ranks = [
        "Civitas Aspirant",
        "Civitas",
        "Legionary",
        "Decanus",
        "Tesserarius",
        "Optio",
        "Centurion",
        "Praetor",
        "Legate"
    ]
    
    current_lower = current.lower()
    matching = [
        app_commands.Choice(name=rank, value=rank)
        for rank in ranks
        if current_lower in rank.lower()
    ]
    
    return matching[:25]


async def autocomplete_paths(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    """
    Autocomplete for progression paths.
    
    Args:
        interaction: Discord interaction
        current: Current input text
    
    Returns:
        List of path choices
    """
    paths = ["pre_induction", "legionary"]
    
    current_lower = current.lower()
    matching = [
        app_commands.Choice(name=path.replace("_", " ").title(), value=path)
        for path in paths
        if current_lower in path.lower()
    ]
    
    return matching[:25]

