# utils/checks.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from typing import Iterable

def cmd_channel_only(*allowed_ids: int):
    """Prefix/hybrid (ctx) – only allows in specified channels."""
    def predicate(ctx: commands.Context) -> bool:
        return bool(ctx.channel and ctx.channel.id in allowed_ids)
    return commands.check(predicate)

def appcmd_channel_only(*allowed_ids: int):
    """Slash (interaction) – only allows in specified channels."""
    async def predicate(interaction: discord.Interaction) -> bool:
        allowed = bool(interaction.channel and interaction.channel.id in allowed_ids)
        if not allowed:
            # Raise error with more descriptive and user-friendly message
            channel_ids_str = ', '.join(str(cid) for cid in allowed_ids)
            current_channel = interaction.channel.name if interaction.channel else 'Unknown'
            # Try to get allowed channel name via bot (will be improved in error handler)
            raise app_commands.CheckFailure(
                f"This command can only be used in a specific channel (ID: {channel_ids_str}). "
                f"You are currently in: #{current_channel} (ID: {interaction.channel.id if interaction.channel else 'None'})"
            )
        return True
    return app_commands.check(predicate)
