# utils/checks.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from typing import Iterable

def cmd_channel_only(*allowed_ids: int):
    """Prefix/hybrid (ctx) – permite apenas nos canais especificados."""
    def predicate(ctx: commands.Context) -> bool:
        return bool(ctx.channel and ctx.channel.id in allowed_ids)
    return commands.check(predicate)

def appcmd_channel_only(*allowed_ids: int):
    """Slash (interaction) – permite apenas nos canais especificados."""
    async def predicate(interaction: discord.Interaction) -> bool:
        allowed = bool(interaction.channel and interaction.channel.id in allowed_ids)
        if not allowed:
            # Levantar erro com mensagem mais descritiva e amigável
            channel_ids_str = ', '.join(str(cid) for cid in allowed_ids)
            current_channel = interaction.channel.name if interaction.channel else 'Unknown'
            # Tentar obter nome do canal permitido via bot (será melhorado no handler de erro)
            raise app_commands.CheckFailure(
                f"Este comando só pode ser usado no canal específico (ID: {channel_ids_str}). "
                f"Você está atualmente em: #{current_channel} (ID: {interaction.channel.id if interaction.channel else 'None'})"
            )
        return True
    return app_commands.check(predicate)
