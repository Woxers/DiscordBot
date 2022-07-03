import datetime
from typing import List
import discord
import logging

from config import Config
from libs import Database
from discord.ext import commands

logger = logging.getLogger(__name__)

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info('Connecting Verification module')

    ###################################
    ##            GRANT MC           ##
    ###################################
    @commands.command(name='grant-mc', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    async def grant_mc(self, ctx, id: int = None):
        if Database.check_user(id):
            Database.set_status(id, 'ACCESS')
            await self.bot.send_embed(ctx.channel, title='Command executed', description=f'<@{id}> has now acces to MC server', color='success')
            await self.bot.get_cog('MessagesCog').have_access_message(self.bot.get_user(id))
        else:
            await self.bot.get_cog('MessagesCog').unexpected_error_message(ctx)

    ###################################
    ##             REJECT            ##
    ###################################
    @commands.command(name='reject', invoke_without_command='True')
    @commands.has_permissions(administrator = True)
    async def reject(self, ctx, id: int = None):
        if Database.check_user(id):
            guild = self.bot.get_guild(Config.get('guild', 'id'))
            Database.set_status(id, 'REJECTED')
            member = guild.get_member(id)
            await member.edit(roles=[]) 
            role = discord.utils.get(member.guild.roles, id=Config.get('role', 'rejected'))
            await member.add_roles(role, reason='Rejected Auto-role')
            nickname = Database.get_user(id)['Nickname']
            if (nickname != ''):
                await self.bot.unregister_player(nickname)
            await self.bot.send_embed(ctx.channel, title='Command executed', description=f'<@{id}> has been rejected', color='success')
        else:
            await self.bot.get_cog('MessagesCog').unexpected_error_message(ctx)

async def setup(bot):
    await bot.add_cog(VerificationCog(bot))