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


def is_moderator_or_owner(interaction: discord.Interaction) -> bool:
    """
    Check if user is a moderator or server owner.
    
    Moderator = has manage_messages permission OR administrator permission
    Owner = server owner (guild.owner)
    
    Args:
        interaction: Discord interaction
    
    Returns:
        True if user is moderator or owner, False otherwise
    """
    if not interaction.guild or not interaction.user:
        return False
    
    # Check if user is server owner
    if interaction.guild.owner_id == interaction.user.id:
        return True
    
    # Check if user is a member (has roles)
    if not isinstance(interaction.user, discord.Member):
        return False
    
    # Check permissions
    perms = interaction.user.guild_permissions
    
    # Moderator = manage_messages OR administrator
    if perms.manage_messages or perms.administrator:
        return True
    
    return False


def appcmd_moderator_or_owner():
    """
    Check decorator for app commands - only allows moderators or server owners.
    
    Usage:
        @appcmd_moderator_or_owner()
        async def my_command(interaction: discord.Interaction):
            ...
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        if not is_moderator_or_owner(interaction):
            raise app_commands.CheckFailure(
                "❌ Você precisa ser **moderador** ou **dono do servidor** para usar este comando.\n"
                "Permissões necessárias: Gerenciar Mensagens ou Administrador."
            )
        return True
    return app_commands.check(predicate)
