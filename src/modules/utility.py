import discord
import asyncio
import logging

from config import Config
from discord.ext import commands

logger = logging.getLogger(__name__)

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        logger.info('Connecting Utility module')

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def set_target_guild(self, ctx):
        Config.set('guild', 'id', ctx.guild.id)
        await self.bot.sendEmbed(ctx, 'This server is now target', None, '0', 'success')
        logging.info(f'The server {ctx.guild} with ID: {ctx.guild.id} is now target')

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def auto_role(self, ctx, action = None, role = None):
        if (action == None):
            await self.send_auto_role(ctx, 'neutral')
            return

        flag = 0
        if (role != None):
            if (role.startswith('<@&')):
                print(role)
                role = role[3:-1]
                print(role)

            if (role.isdigit()):
                role = int(role)
                role = discord.utils.get(ctx.guild.roles,id=role)
            else:
                role = discord.utils.get(ctx.guild.roles,name=role)
        
        if (type(role) == discord.role.Role):
            flag = 1
            role = role.id
        
        if (action == 'set'):
            if (flag):
                Config.set('role', 'id', role)
                await self.send_auto_role(ctx, 'success')
            else:
                await self.bot.sendEmbed(ctx, 'Error', 'Invalid using of command, see example:\n\n!auto_role [add|remove|enable|disable] <role>', '0', 'error')
        elif (action == 'remove'):
            Config.set('role', 'enabled', 0)
            Config.set('role', 'id', 0)
            await self.send_auto_role(ctx, 'success')
        elif (action == 'enable'):
            Config.set('role', 'enabled', 1)
            await self.send_auto_role(ctx, 'success')
        elif (action == 'disable'):
            Config.set('role', 'enabled', 0)
            await self.send_auto_role(ctx, 'success')
        else:
            await self.bot.sendEmbed(ctx, 'Error', 'Invalid using of command, see example:\n\n!auto_role [add/remove/enable/disable] [role]', '0', 'error')
            return

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

    async def send_auto_role(self, ctx, color):
        enabled = Config.get('role', 'enabled')
        enabled = 'true' if (enabled) else 'false'
        role = Config.get('role', 'id')
        role = '<@&' + str(role) + '>' if (role != 0) else 'not set'
        await self.bot.sendEmbed(ctx, 'Auto-Role', f'Enabled: {enabled}\nRole: {role}', '0', color)