import discord
from discord import app_commands
from bot import client
from utils.database import get_user, create_user, update_points

@client.tree.command(name="add", description="Adiciona pontos a um usuário.")
async def add(interaction: discord.Interaction, member: discord.Member, points: int):
    await interaction.response.defer(thinking=True)

    user = await get_user(member.id)
    if user is None:
        await create_user(member.id)

    await update_points(member.id, points)
    user = await get_user(member.id)

    await interaction.followup.send(f"{member.name} agora tem {user[1]} pontos.")