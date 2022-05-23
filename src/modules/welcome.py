import discord
import asyncio
import logging

from config import Config
from discord.ext import commands

logger = logging.getLogger(__name__)

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        logger.info('Connecting Verification module')

    @commands.Cog.listener()
    async def on_ready(self):
        print("WelcomeCog Listener on ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'player join: {member.mention}')
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'player left: {member.mention}')
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Goodbye {member.mention}.')