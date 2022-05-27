import discord
import logging
import asyncio
import datetime

from config import Config
from discord.ext import commands

logger = logging.getLogger(__name__)

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        logger.info('Connecting Utility module')

    @commands.group(name='test1', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def test1(self, ctx, arg = None):
        await self.bot.get_cog('VerificationCog').new_player_message(ctx.author)

    ###################################
    ##      Command Target-guild     ##
    ###################################
    @commands.group(name='target-guild', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def target_guild(self, ctx, arg = None):
        if (arg == None):
            guild = self.bot.get_guild(Config.get('guild', 'id'))
            await self.bot.sendEmbed(ctx, 'Target-Guild', f'Guild: {guild}\n\n!target-guild [set]', '0', 'neutral')
        else:
            await self.bot.sendEmbed(ctx, 'Error', 'Incorrect using of command, see example:\n\n!target-guild [set]', '0', 'error')
            
    @target_guild.command(name='set')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def target_guild_set(self, ctx, arg = None):
        if (Config.get('guild', 'id') == ctx.guild.id):
            await self.bot.sendEmbed(ctx, 'Error', 'This server is already target', '0', 'error')
            return
        Config.set('guild', 'id', ctx.guild.id)
        logger.info(f'The server {ctx.guild} with ID: {ctx.guild.id} is now target, admin: {ctx.author.id}')
        await self.bot.sendEmbed(ctx, 'Command executed', 'This server is now target', '0', 'success')


    ###################################
    ##       Command Auto-role       ##
    ###################################
    @commands.group(name='auto-role', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role(self, ctx, arg = None):
        if (arg == None):
            enabled = Config.get('role', 'enabled')
            enabled = 'true' if (enabled) else 'false'
            role = Config.get('role', 'id')
            role = '<@&' + str(role) + '>' if (role != 0) else 'not set'
            await self.bot.sendEmbed(ctx, 'Auto-Role', f'Enabled: {enabled}\nRole: {role} \n\n!auto_role [set|remove|enable|disable] <role>', '0', 'neutral')
        else:
            await self.bot.sendEmbed(ctx, 'Error', 'Incorrect using of command, see example:\n\n!auto_role [set|remove|enable|disable] <role>', '0', 'error')
    
    @auto_role.command(name='set')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_set(self, ctx, role = None):
        flag = 0
        if (role != None):
            if (role.startswith('<@&')):
                role = role[3:-1]

            if (role.isdigit()):
                role = int(role)
                role = discord.utils.get(ctx.guild.roles,id=role)
            else:
                role = discord.utils.get(ctx.guild.roles,name=role)

        if (type(role) == discord.role.Role):
            flag = 1
            role = role.id

        if (flag):
            Config.set('role', 'id', role)
            logger.info(f'Auto-role set to <@&{role}>, admin: {ctx.author.id}')
            await self.bot.sendEmbed(ctx, 'Command executed', f'Auto-role set to <@&{role}>', '0', 'success')
        else:
            await self.bot.sendEmbed(ctx, 'Error', 'Incorrect using of command, see example:\n\n!auto_role [set|remove|enable|disable] <role>', '0', 'error')

    @auto_role.command(name='remove')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_remove(self, ctx):
        Config.set('role', 'enabled', 0)
        Config.set('role', 'id', 0)
        logger.info(f'Auto-role removed, admin={ctx.author.id}')
        await self.bot.sendEmbed(ctx, 'Command executed', f'Auto-role removed', '0', 'success')

    @auto_role.command(name='enable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_enable(self, ctx):
        Config.set('role', 'enabled', 1)
        logger.info(f'Auto-role enabled, admin={ctx.author.id}')
        await self.bot.sendEmbed(ctx, 'Command executed', f'Auto-role enabled', '0', 'success')
    
    @auto_role.command(name='disable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_disable(self, ctx):
        Config.set('role', 'enabled', 0)
        logger.info(f'Auto-role disabled, admin={ctx.author.id}')
        await self.bot.sendEmbed(ctx, 'Command executed', f'Auto-role disabled', '0', 'success')

    ###################################
    ##       Command Join-leave       ##
    ###################################
    @commands.group(name='join-leave', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave(self, ctx, arg = None):
        if (arg == None):
            enabled = Config.get('greetings', 'enabled')
            enabled = 'true' if (enabled) else 'false'
            channel = Config.get('greetings', 'id')
            channel = '<#' + str(channel) + '>' if (channel != 0) else 'not set'
            await self.bot.sendEmbed(ctx, 'Join-Leave', f'Enabled: {enabled}\nChannel: {channel} \n\n!join-leave [channel|enable|disable] #<channel>', '0', 'neutral')
        else:
            await self.bot.sendEmbed(ctx, 'Error', 'Incorrect using of command, see example:\n\n!join-leave [channel|enable|disable] #<channel>', '0', 'error')

    @join_leave.command(name='enable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave_enable(self, ctx):
        Config.set('greetings', 'enabled', 1)
        logger.info(f'Join-leave enabled, admin={ctx.author.id}')
        await self.bot.sendEmbed(ctx, 'Command executed', f'Join-leave enabled', '0', 'success')
    
    @join_leave.command(name='disable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave_disable(self, ctx):
        Config.set('greetings', 'enabled', 0)
        logger.info(f'Join-leave disabled, admin={ctx.author.id}')
        await self.bot.sendEmbed(ctx, 'Command executed', f'Join-leave disabled', '0', 'success')

    @join_leave.command(name='channel')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave_channel(self, ctx, channel: str = None):
        if (channel == None):
            await self.bot.sendEmbed(ctx, 'Join-Leave', f'Channel: <#{channel}> \n\n!join-leave [channel|enable|disable] #<channel>', '0', 'neutral')
            return
        if not (channel.startswith('<#')):
            await self.bot.sendEmbed(ctx, 'Error', 'Incorrect using of command, see example:\n\n!join-leave [channel|enable|disable] #<channel>', '0', 'error')
            return
        channel = channel[2:-1]
        Config.set('greetings', 'id', int(channel))
        logger.info(f'Join-leave channel set to {channel}, admin={ctx.author.id}')
        logsChannel = self.bot.get_channel(int(channel))
        embed = discord.Embed(title = f'Join-Leave', color = Config.getColor('success'))
        embed.set_author(name="Advanced Manager", icon_url="https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702")
        embed.description = 'This channel is now using for join-leave logs'
        embed.set_footer(text='GameSpace#Private \u200b')
        embed.timestamp = timestamp=datetime.datetime.utcnow()
        await logsChannel.send(embed= embed)
        await self.bot.sendEmbed(ctx, 'Command executed', f'Join-leave channel set to <#{channel}>', '0', 'success')

    ###################################
    ##          Command Ping         ##
    ###################################
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ping(self, ctx):
        msg = await ctx.send(f'pong in {round(self.bot.latency * 1000)} ms!')
        await asyncio.sleep(5)
        await msg.delete()

    @ping.error
    async def ping_error(self, ctx, error):
        if (str(ctx.channel).startswith("Direct Message with")):
            return
        msg = await ctx.send(embed = discord.Embed(description = f'{error}', color = int(Config.get('embed', 'accent_color'), 16)))
        await asyncio.sleep(5)
        await msg.delete()

def setup(bot):
    bot.add_cog(UtilityCog(bot))