import discord

from discord.ext import commands

from logger import log_error, log_info
from config import get_color, config

from database import Database

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("Welcome Module successfully loaded")

    @commands.command(name='test')
    @commands.has_permissions(administrator = True)
    async def test(self, ctx, arg = None):
        dt = dict()
        dt['USER_NAME'] = 'Aptem'
        dt['USER_MENTION'] = '<@222746438814138368>'
        dt['URL'] = 'https://ictis.alex-b.me/'
        dt['COLOR'] = get_color('neutral')
        dt['TIMESTAMP'] = '2022-07-15 13:04:06'
        await self.bot.send_json_embed(ctx, 'example/key.txt', replace_dict=dt, delete_after = 10)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))