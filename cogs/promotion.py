"""
Promotion Cog - Sistema de promoções com integração Roblox.

Gerencia promoções de membros, incluindo integração com grupo Roblox
e mensagens de reconhecimento personalizadas.
"""

from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from services.bloxlink_service import BloxlinkService
from services.progression_service import ProgressionService
from services.audit_service import AuditService
from utils.checks import cmd_channel_only, appcmd_channel_only
from utils.config import STAFF_CMDS_CHANNEL_ID, GUILD_ID
from utils.logger import get_logger
import os

logger = get_logger(__name__)


class PromotionCog(commands.Cog):
    """Cog para gerenciar promoções de membros"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bloxlink_service = BloxlinkService()
        self.progression_service = ProgressionService()
        self.audit_service = AuditService()
        self.roblox_group_id = os.getenv("ROBLOX_GROUP_ID", "")
        self.roblox_cookie = os.getenv("ROBLOX_COOKIE", "")
    
    @app_commands.command(name="promote", description="Promove um membro para um novo cargo")
    @app_commands.describe(
        member="Membro do Discord para promover",
        new_rank="Novo cargo/rank",
        reason="Razão da promoção (opcional)"
    )
    @appcmd_channel_only(STAFF_CMDS_CHANNEL_ID)
    @app_commands.checks.has_permissions(administrator=True)
    async def promote(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        new_rank: str,
        reason: str = ""
    ):
        """
        Promove um membro para um novo cargo.
        
        Requisitos:
        - Membro deve estar verificado pelo Bloxlink
        - Usuário deve ter permissão administrativa
        - Membro deve ter pontos suficientes (se aplicável)
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
            
            # Obter informações atuais do usuário
            user_info = await self.progression_service.get_user_info(member.id)
            current_rank = user_info.get("rank", "Unknown")
            current_points = user_info.get("points", 0)
            
            # Atualizar rank no sistema
            await self.progression_service.set_rank(
                user_id=member.id,
                rank=new_rank,
                set_by=interaction.user.id
            )
            
            # Extrair informações do Roblox
            roblox_username = roblox_data.get("username", "Unknown")
            roblox_id = roblox_data.get("id", "Unknown")
            avatar_url = roblox_data.get("avatar_url", member.display_avatar.url)
            
            # Criar embed de promoção
            embed = discord.Embed(
                title="⚔️ Promoção concedida ⚔️",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )
            
            # Informações do usuário
            embed.add_field(
                name="Usuário",
                value=f"**{roblox_username}**\n`ID: {roblox_id}`",
                inline=True
            )
            
            embed.add_field(
                name="Progressão",
                value=f"**{current_points}** pontos",
                inline=True
            )
            
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            
            # Promoção
            embed.add_field(
                name="De",
                value=f"**{current_rank}**",
                inline=True
            )
            
            embed.add_field(
                name="→",
                value="⬇️",
                inline=True
            )
            
            embed.add_field(
                name="Para",
                value=f"**{new_rank}**",
                inline=True
            )
            
            # Razão (se fornecida)
            if reason:
                embed.add_field(
                    name="Razão",
                    value=reason,
                    inline=False
                )
            
            # Avatar
            embed.set_thumbnail(url=avatar_url)
            
            # Mensagem de reconhecimento
            recognition_message = (
                "*Continue servindo com honra sob o estandarte do Age Of Warfare.*"
            )
            
            embed.add_field(
                name="\u200b",
                value=recognition_message,
                inline=False
            )
            
            # Footer
            embed.set_footer(
                text=f"Promovido por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            
            # Enviar mensagem
            await interaction.followup.send(embed=embed)
            
            # TODO: Integração com Roblox Group API para promover no grupo
            # if self.roblox_group_id and self.roblox_cookie:
            #     await self._promote_in_roblox_group(roblox_id, new_rank)
            
            # Log de auditoria
            await self.audit_service.log_operation(
                user_id=member.id,
                action_type="UPDATE",
                data_type="rank",
                performed_by=interaction.user.id,
                purpose="Promoção de cargo",
                details={
                    "old_rank": current_rank,
                    "new_rank": new_rank,
                    "points": current_points,
                    "roblox_username": roblox_username,
                    "roblox_id": roblox_id,
                    "reason": reason
                }
            )
            
            logger.info(
                f"User {member.id} ({roblox_username}) promoted from {current_rank} "
                f"to {new_rank} by {interaction.user.id}"
            )
            
        except Exception as e:
            logger.error(f"Error in promote command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao promover membro. Verifique os logs.",
                ephemeral=True
            )
    
    async def _promote_in_roblox_group(
        self,
        roblox_id: int,
        rank: str
    ) -> bool:
        """
        Promove usuário no grupo Roblox (implementação futura).
        
        Args:
            roblox_id: Roblox user ID
            rank: Rank name
        
        Returns:
            True if successful, False otherwise
        """
        # TODO: Implementar integração com Roblox Group API
        # Requer autenticação com cookie e permissões de grupo
        logger.info(f"TODO: Promote {roblox_id} to {rank} in Roblox group {self.roblox_group_id}")
        return False


async def setup(bot: commands.Bot):
    await bot.add_cog(PromotionCog(bot))

