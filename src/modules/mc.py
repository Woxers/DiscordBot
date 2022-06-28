import logging

from config import Config
from discord.ext import commands

from libs import Database

logger = logging.getLogger(__name__)

class McCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def player_joined(self, nickname):
        print(nickname + ' joined the server')

    async def player_left(self, nickname):
        print(nickname + ' left the server')

    async def player_login(self, nickname):
        print(nickname + ' logged in')

    async def player_failed_login(self, nickname):
        print(nickname + ' failed login')

async def setup(bot):
    await bot.add_cog(McCog(bot))