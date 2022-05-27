import os
import discord
import asyncio
import logging
import datetime

from discord.ext import commands
from help import CustomHelpCommand
from config import Config

import log

class CustomBot(commands.Bot):
    def __init__(self):
        helpCommand = CustomHelpCommand()
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand, intents=intents)
        intents.members = True
        self.setupCogs()

    async def on_ready(self): 
        print('Bot connected successfully!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.sendEmbed(ctx, 'Command not found', None, 3, 'error')

    def setupCogs(self):
        for filename in os.listdir('./modules'):
            if filename.endswith('.py') and not filename.startswith('__'):
                self.load_extension(f'modules.{filename[:-3]}')
                print(f'load: {filename[:-3]}')
            else:
                print(f'Unable to load {filename[:-3]}')

    async def sendEmbed(self, ctx, title = None, description = None, duration = 0, color = None):
        embed = discord.Embed(title = f'{title}', color = Config.getColor(color))
        if (description != None):
            embed.description = description
        msg = await ctx.send(embed = embed)
        if (duration > 0):
            await asyncio.sleep(duration)
            await msg.delete()

bot = CustomBot()

bot.run(Config.get('bot', 'token'))