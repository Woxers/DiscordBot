import discord

from logger import log_error, log_info
from config import get_color, config
#from libs import Database
from discord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("Welcome Module succesfully loaded")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))