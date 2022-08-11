import asyncio
import discord
from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

from discord.ui import Button, View

from database import Database

from .utils.menu_message import MenuMessage

class UserMenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("UserMenu Module successfully loaded!")

    @commands.command(name='menu')
    @commands.is_owner() 
    async def menu_command(self, ctx, *args):
        print(1)
        try:
            menuMessage = MenuMessage(self.bot)
        except Exception as e:
            print(e)
        print(2)
        menuMessage.channel = ctx.channel
        print(3)
        await menuMessage.send_menu_message()

async def setup(bot):
    await bot.add_cog(UserMenuCog(bot))