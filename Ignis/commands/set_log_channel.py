import discord
from discord import app_commands
from bot import client

@client.tree.command(name="set_log_channel", description="Configura o canal de logs.")
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    client.log_channel_id = channel.id
    await interaction.response.send_message(f"Canal de logs configurado para: {channel.mention}")