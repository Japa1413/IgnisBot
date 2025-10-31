import discord

async def handle_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, log_channel_id: int):
    channel = member.guild.get_channel(log_channel_id)
    if not channel:
        return  # Channel not found, exit

    if before.channel is None and after.channel is not None:
        # Member joined a voice channel
        embed = discord.Embed(
            title='Member Joined',
            description=f'{member.mention} joined {after.channel.mention}',
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

    elif before.channel is not None and after.channel is None:
        # Member left a voice channel
        embed = discord.Embed(
            title='Member Left',
            description=f'{member.mention} left {before.channel.mention}',
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

    elif before.channel is not None and after.channel is not None:
        # Member moved between channels
        if before.channel != after.channel:
            embed = discord.Embed(
                title='Member Moved',
                description=f'{member.mention} moved from {before.channel.mention} to {after.channel.mention}',
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)

        # Deafened/Undeafened
        if before.deaf != after.deaf:
            action = 'Deafened' if after.deaf else 'Undeafened'
            embed = discord.Embed(
                title=f'Member {action}',
                description=f'{member.mention} was {action.lower()} in {after.channel.mention}',
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)

        # Muted/Unmuted
        elif before.mute != after.mute:
            action = 'Muted' if after.mute else 'Unmuted'
            embed = discord.Embed(
                title=f'Member {action}',
                description=f'{member.mention} was {action.lower()} in {after.channel.mention}',
                color=discord.Color.purple()
            )
            await channel.send(embed=embed)