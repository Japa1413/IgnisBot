"""
Induction Cog - Processo de indução para novos membros.

Gerencia o processo de indução com integração Bloxlink,
exibindo informações do Roblox e iniciando o processo.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from services.bloxlink_service import BloxlinkService
from services.audit_service import AuditService
from utils.checks import cmd_channel_only, appcmd_channel_only, appcmd_moderator_or_owner
from utils.config import GUILD_ID
from utils.logger import get_logger

logger = get_logger(__name__)

# Canal específico para comandos de indução e promoção
INDUCTION_CHANNEL_ID = 1375941286267326532


class InductionCog(commands.Cog):
    """Cog para gerenciar processo de indução"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        self.audit_service = AuditService()
    
    @app_commands.command(name="induction", description="Inicia processo de indução para um jogador")
    @app_commands.describe(
        roblox_username="Nickname do jogador no Roblox",
        instructions="Instruções adicionais (opcional)"
    )
    @appcmd_channel_only(INDUCTION_CHANNEL_ID)
    @appcmd_moderator_or_owner()
    async def induction(
        self,
        interaction: discord.Interaction,
        roblox_username: str,
        instructions: str = ""
    ):
        """
        Inicia processo de indução para um jogador pelo nickname do Roblox.
        
        Requisitos:
        - Nickname do Roblox válido
        - Usuário deve ser moderador ou dono do servidor
        - Comando deve ser usado no canal específico
        """
        await interaction.response.defer(thinking=True, ephemeral=False)
        
        try:
            # Buscar informações do Roblox pelo username
            searched_username = roblox_username.strip()
            roblox_data = await self.bloxlink_service.get_roblox_user_by_username(searched_username)
            
            if not roblox_data:
                await interaction.followup.send(
                    f"❌ Usuário **{searched_username}** não encontrado no Roblox.\n"
                    f"Verifique se o nickname está correto (não use display name).",
                    ephemeral=True
                )
                return
            
            # Extrair informações
            roblox_username_found = roblox_data.get("username", "Unknown")
            roblox_id = roblox_data.get("id", "Unknown")
            avatar_url = roblox_data.get("avatar_url", "")
            
            # Criar embed de indução
            embed = discord.Embed(
                title="🔥 Iniciando processo de indução 🔥",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            
            # Adicionar informações do recruta
            embed.add_field(
                name="Recruta",
                value=f"**{roblox_username_found}**",
                inline=True
            )
            
            embed.add_field(
                name="ID Roblox",
                value=f"`{roblox_id}`",
                inline=True
            )
            
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            # Avatar
            embed.set_thumbnail(url=avatar_url)
            
            # Mensagem de boas-vindas
            welcome_message = (
                f"Bem-vindo ao processo de indução do **Age Of Warfare**.\n"
                f"Você será guiado através de uma série de etapas para se tornar um membro oficial do grupo.\n\n"
                f"**Próximos passos:**\n"
            )
            
            if instructions:
                welcome_message += f"{instructions}\n\n"
            else:
                welcome_message += (
                    "1. Leia as regras do servidor\n"
                    "2. Complete o treinamento básico\n"
                    "3. Aguarde aprovação da administração\n\n"
                )
            
            welcome_message += (
                "Siga atentamente as instruções fornecidas.\n"
                "Qualquer dúvida, entre em contato com a administração."
            )
            
            embed.add_field(
                name="📋 Instruções",
                value=welcome_message,
                inline=False
            )
            
            # Footer
            embed.set_footer(
                text=f"Iniciado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Enviar mensagem
            await interaction.followup.send(embed=embed)
            
            # Log de auditoria
            await self.audit_service.log_operation(
                user_id=0,  # Não temos Discord ID, apenas Roblox username
                action_type="CREATE",
                data_type="induction",
                performed_by=interaction.user.id,
                purpose="Início do processo de indução",
                details={
                    "roblox_username": roblox_username_found,
                    "roblox_id": roblox_id,
                    "instructions": instructions,
                    "searched_username": searched_username
                }
            )
            
            logger.info(
                f"Induction started for Roblox user {roblox_username_found} (ID: {roblox_id}) "
                f"by {interaction.user.id}"
            )
            
        except Exception as e:
            logger.error(f"Error in induction command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao iniciar processo de indução. Verifique os logs.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(InductionCog(bot))

