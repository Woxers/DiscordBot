import discord
import asyncio
import logging
import datetime

from discord.ext import commands
from config import Config

# Initialize logger
path = Config.get('log', 'path') + str(datetime.datetime.now().date()) + '.log'
logging.basicConfig(filename=path,format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%y-%m-%d %H:%M:%S', encoding='utf-8', level=20)
logging.info('Start logging')

from libs import Database
from modules import UtilityCog, CustomHelpCommand
from libs import Database

class CustomBot(commands.Bot):
    def __init__(self):
        helpCommand = CustomHelpCommand()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand)

    async def on_ready(self): 
        logging.info('Bot connected successfully!')
        print('Bot connected successfully!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            msg = await ctx.send(embed = discord.Embed(description = f'Command not found', color = int(Config.get('embed', 'accent_color'), 16)))
            await asyncio.sleep(3)
            await msg.delete()

# Подключение модули
def setupCogs(CustomBot):
    bot.add_cog(UtilityCog(bot))

bot = CustomBot()
setupCogs(bot)

bot.run(Config.get('bot', 'token'))