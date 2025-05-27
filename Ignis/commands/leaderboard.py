import discord
from discord import app_commands
from bot import client
import aiosqlite

@client.tree.command(name="leaderboard", description="Exibe os 10 usuários com mais pontos.")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    async with aiosqlite.connect("ignis.db") as db:
        async with db.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10") as cursor:
            leaderboard = await cursor.fetchall()

    if not leaderboard:
        await interaction.followup.send("A leaderboard está vazia no momento.")
        return

    message = "**Leaderboard:**\n"
    for i, (user_id, points) in enumerate(leaderboard, start=1):
        try:
            user = await client.fetch_user(user_id)
            message += f"{i}. {user.name} - {points} pontos\n"
        except discord.NotFound:
            message += f"{i}. [Usuário desconhecido] - {points} pontos\n"

    await interaction.followup.send(message)