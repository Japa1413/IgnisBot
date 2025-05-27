import discord
from discord.ext import commands
from discord import app_commands

class VCLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="vc_log",
        description="Adiciona pontos a todos os usuários em um canal de voz."
    )
    @app_commands.describe(
        amount="Quantos pontos adicionar",
        event="O evento ou razão para o registro",
        evidence="Anexo como evidência (imagem, captura de tela, etc.)",
        voice_channel="Mencione o canal de voz (opcional, padrão é o canal atual do autor)"
    )
    async def vc_log(
        self,
        interaction: discord.Interaction,
        amount: int,
        event: str,
        evidence: discord.Attachment,
        voice_channel: discord.VoiceChannel = None
    ):
        await interaction.response.defer(thinking=True)

        # Use o canal de voz mencionado ou o canal atual do autor
        if voice_channel is None:
            if interaction.user.voice and interaction.user.voice.channel:
                voice_channel = interaction.user.voice.channel
            else:
                await interaction.followup.send("Você não está em um canal de voz e nenhum canal foi mencionado.")
                return

        # Obtenha os membros no canal de voz
        members = voice_channel.members
        if not members:
            await interaction.followup.send(f"O canal de voz {voice_channel.name} está vazio.")
            return

        # Distribua os pontos para os membros
        for member in members:
            # Aqui você pode adicionar a lógica para atualizar os pontos no banco de dados
            print(f"Adicionando {amount} pontos para {member.name}")

        # Responda ao comando
        await interaction.followup.send(
            f"{amount} pontos foram adicionados para os usuários no canal de voz {voice_channel.name}."
        )

# Adicione a classe ao bot
async def setup(bot):
    await bot.add_cog(VCLogCog(bot))