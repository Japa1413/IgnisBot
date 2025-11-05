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
from utils.checks import cmd_channel_only, appcmd_channel_only
from utils.config import STAFF_CMDS_CHANNEL_ID, GUILD_ID
from utils.logger import get_logger

logger = get_logger(__name__)


class InductionCog(commands.Cog):
    """Cog para gerenciar processo de indução"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        self.audit_service = AuditService()
    
    @app_commands.command(name="induction", description="Inicia processo de indução para um membro")
    @app_commands.describe(
        member="Membro do Discord para iniciar indução",
        instructions="Instruções adicionais (opcional)"
    )
    @appcmd_channel_only(STAFF_CMDS_CHANNEL_ID)
    @app_commands.checks.has_permissions(administrator=True)
    async def induction(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        instructions: str = ""
    ):
        """
        Inicia processo de indução para um membro.
        
        Requisitos:
        - Membro deve estar verificado pelo Bloxlink
        - Usuário deve ter permissão administrativa
        """
        await interaction.response.defer(thinking=True, ephemeral=False)
        
        try:
            # Verificar se membro está no servidor
            if not member.guild:
                await interaction.followup.send("❌ Membro não encontrado no servidor.", ephemeral=True)
                return
            
            # Verificar verificação Bloxlink
            roblox_data = await self.bloxlink_service.get_roblox_user(member.id, GUILD_ID)
            
            if not roblox_data:
                await interaction.followup.send(
                    f"❌ **{member.mention}** não está verificado pelo Bloxlink.\n"
                    f"Por favor, peça para o membro usar `/verify` no Bloxlink primeiro.",
                    ephemeral=True
                )
                return
            
            # Extrair informações
            roblox_username = roblox_data.get("username", "Unknown")
            roblox_id = roblox_data.get("id", "Unknown")
            avatar_url = roblox_data.get("avatar_url", member.display_avatar.url)
            
            # Criar embed de indução
            embed = discord.Embed(
                title="🔥 Iniciando processo de indução 🔥",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            
            # Adicionar informações do recruta
            embed.add_field(
                name="Recruta",
                value=f"**{roblox_username}**",
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
                user_id=member.id,
                action_type="CREATE",
                data_type="induction",
                performed_by=interaction.user.id,
                purpose="Início do processo de indução",
                details={
                    "roblox_username": roblox_username,
                    "roblox_id": roblox_id,
                    "instructions": instructions
                }
            )
            
            logger.info(
                f"Induction started for {member.id} ({roblox_username}) "
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

