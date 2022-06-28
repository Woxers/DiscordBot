import json
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

    @commands.command(name='test1')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def test1(self, ctx, arg = None):
        #await self.bot.get_cog('MessagesCog').new_player_message(ctx.author)
        data = {"content": 'test', "embeds": [
    {
      "title": "Вы зашли на сервер.",
      "description": "Для того, чтобы выполнить быстрый вход нажмите на кнопку ниже:",
      "color": 16777215
    }]}
        await ctx.send('works')
        await ctx.send(content = data)

    ###################################
    ##      Command Target-guild     ##
    ###################################
    @commands.group(name='target-guild', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def target_guild(self, ctx, arg = None):
        if (arg == None):
            guild = self.bot.get_guild(Config.get('guild', 'id'))
            await self.bot.send_embed(ctx.channel, title='Target-Guild', description=f'Guild: {guild}\n\n!target-guild [set]', color='neutral')
        else:
            await self.bot.send_embed(ctx.channel, title='Error', description='Incorrect using of command, see example:\n\n!target-guild [set]', color='error')
            
    @target_guild.command(name='set')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def target_guild_set(self, ctx, arg = None):
        if (Config.get('guild', 'id') == ctx.guild.id):
            await self.bot.send_embed(ctx.channel, title='Error', description='This server is already target', color='error')
            return
        Config.set('guild', 'id', ctx.guild.id)
        logger.info(f'The server {ctx.guild} with ID: {ctx.guild.id} is now target, admin: {ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description='This server is now target', color='success')


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
            await self.bot.send_embed(ctx.channel, title='Auto-Role', description=f'Enabled: {enabled}\nRole: {role} \n\n!auto_role [set|remove|enable|disable] <role>', color='neutral')
        else:
            await self.bot.send_embed(ctx.channel, title='Error', description='Incorrect using of command, see example:\n\n!auto_role [set|remove|enable|disable] <role>', color='error')
    
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
            await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Auto-role set to <@&{role}>', color='success')
        else:
            await self.bot.send_embed(ctx.channel, title='Error', description='Incorrect using of command, see example:\n\n!auto_role [set|remove|enable|disable] <role>', color='error')

    @auto_role.command(name='remove')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_remove(self, ctx):
        Config.set('role', 'enabled', 0)
        Config.set('role', 'id', 0)
        logger.info(f'Auto-role removed, admin={ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Auto-role removed', color='success')

    @auto_role.command(name='enable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_enable(self, ctx):
        Config.set('role', 'enabled', 1)
        logger.info(f'Auto-role enabled, admin={ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Auto-role enabled', color='success')
    
    @auto_role.command(name='disable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def auto_role_disable(self, ctx):
        Config.set('role', 'enabled', 0)
        logger.info(f'Auto-role disabled, admin={ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Auto-role disabled', color='success')

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
            await self.bot.send_embed(ctx.channel, title='Join-Leave', description=f'Enabled: {enabled}\nChannel: {channel} \n\n!join-leave [channel|enable|disable] #<channel>', color='neutral')
        else:
            await self.bot.send_embed(ctx.channel, title='Error', description='Incorrect using of command, see example:\n\n!join-leave [channel|enable|disable] #<channel>', color='error')

    @join_leave.command(name='enable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave_enable(self, ctx):
        Config.set('greetings', 'enabled', 1)
        logger.info(f'Join-leave enabled, admin={ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Join-leave enabled', color='success')
    
    @join_leave.command(name='disable')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave_disable(self, ctx):
        Config.set('greetings', 'enabled', 0)
        logger.info(f'Join-leave disabled, admin={ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Join-leave disabled', color='success')

    @join_leave.command(name='channel')
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def join_leave_channel(self, ctx, channel: str = None):
        if (channel == None):
            await self.bot.send_embed(ctx.channel, title='Join-Leave', description=f'Channel: <#{channel}> \n\n!join-leave [channel|enable|disable] #<channel>', color='neutral')
            return
        if not (channel.startswith('<#')):
            await self.bot.send_embed(ctx.channel, title='Error', description='Incorrect using of command, see example:\n\n!join-leave [channel|enable|disable] #<channel>', color='error')
            return
        channel = channel[2:-1]
        Config.set('greetings', 'id', int(channel))
        logger.info(f'Join-leave channel set to {channel}, admin={ctx.author.id}')
        await self.bot.send_embed(ctx.channel, title='Command executed', description=f'Join-leave channel set to <#{channel}>', color='success')


    ###################################
    ##          Command Ping         ##
    ###################################
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ping(self, ctx):
        await self.bot.send_embed(ctx.channel, title='Ping', description=f'pong in {round(self.bot.latency * 1000)} ms!', color='success', duration= 5)

    @ping.error
    async def ping_error(self, ctx, error):
        if (str(ctx.channel).startswith("Direct Message with")):
            return
        await self.bot.send_embed(ctx.channel, title='Error', description=f'{error}', color='error', duration= 5)


    ###################################
    ##        Command Invites        ##
    ###################################
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def invites(self, ctx):
        inv = ''
        for invite in self.bot.get_invites():
            inv += f'({invite.uses}) {str(invite)[19:]} - Владелец {invite.inviter.mention}\n'
        await self.bot.send_embed(ctx.channel, title='Invites', description=inv, color='neutral')

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))