import discord
import asyncio
import logging
import datetime

from discord.ext import commands
from config import Config

# Initialize logger
path = Config.get('log', 'path') + str(datetime.datetime.now().date()) + '.log'
logging.basicConfig(filename=path,format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%y-%m-%d %H:%M:%S', encoding='utf-8')
logging.warning('Start logging')

from libs import Database
from modules import UtilityCog

class CustomBot(commands.Bot):
    def __init__(self):
        helpCommand = CustomHelpCommand()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand)

    async def on_ready(self): 
        print('Bot connected successfully!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            msg = await ctx.send(embed = discord.Embed(description = f'Command not found', color = int(Config.get('embed', 'accent_color'), 16)))
            await asyncio.sleep(3)
            await msg.delete()

# TODO: Перенести в отдельный файл
class CustomHelpCommand(commands.HelpCommand):
    helpPages = [['Utility', '- ping\n- hello\n- hi @someone'], ['Test', '- ping\n- hello\n- hi @someone']]

    async def send_bot_help(self, mapping):
        # Embed generator for python:
        # https://cog-creators.github.io/discord-embed-sandbox/
        destination = self.get_destination()
        embededMessage = discord.Embed(title='Help Command')
        for page in self.helpPages:
            embededMessage.add_field(name=page[0], value=page[1])
        await destination.send(embed=embededMessage)
        return await super().send_bot_help(mapping)
    
    async def command_not_found(self, ctx, *, command=None):
        # Command not found
        print("command_not_found")
        return await super().command_callback(ctx, command=command)

# Подключение модули
def setupCogs(CustomBot):
    bot.add_cog(UtilityCog(bot))

bot = CustomBot()
setupCogs(bot)

bot.run(Config.get('bot', 'token'))