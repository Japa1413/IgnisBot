from bot import client  # Importe o client do módulo bot
import discord

@client.event
async def on_member_join(member):
    if client.log_channel_id is not None:
        log_channel = client.get_channel(client.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Member Joined",
                description=f"{member.mention} entrou no servidor.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"User ID: {member.id}")
            await log_channel.send(embed=embed)