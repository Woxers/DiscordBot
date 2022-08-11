from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

from .utils.database.players_db import PlayersDatabase
from .utils.menu_message import MenuMessage

from .utils.menu.main_page import MainPage

class MenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("Menu Module successfully loaded!")

    @commands.command(name='menu')
    @commands.is_owner() 
    async def menu_command(self, ctx, *args):
        menu_message = MenuMessage(self.bot, ctx.author, ctx.channel)
        try:
            await menu_message.setup_menu_message()
        except Exception as e:
            log_error(e)
            raise(e)
        # try:
        #     menuMessage = MenuMessage(self.bot)
        #     menuMessage.channel = ctx.channel
        #     menuMessage.user = ctx.author
        #     await menuMessage.build_message('base')
        # except Exception as e:
        #     print(e)
    
    @menu_command.error
    async def menu_command_error(self, ctx, error):
        await self.bot.send_simple_embed(ctx.channel, title='Непредвиденная ошибка!', description=f'Пожалуйста, обратитесь к администратору <@222746438814138368>, чтобы решить эту проблему.', color='error')

async def setup(bot):
    await bot.add_cog(MenuCog(bot))