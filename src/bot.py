import discord
import asyncio
import logging
import datetime

from discord.ext import commands
from config import Config

import log

from modules import WelcomeCog, UtilityCog, CustomHelpCommand, VerificationCog
from libs import Database

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
        self.add_cog(UtilityCog(self))
        self.add_cog(WelcomeCog(self))
        self.add_cog(VerificationCog(self))

    async def sendEmbed(self, ctx, title = None, description = None, duration = None, color = None):
        embed = discord.Embed(title = f'{title}', color = Config.getColor(color))
        #embed.set_author(name="Advanced Manager", icon_url="https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702")
        if (description != None):
            embed.description = description
        #embed.set_footer(text='GS#Private - Vanilla MC \u200b')
        #embed.timestamp = timestamp=datetime.datetime.utcnow()
        msg = await ctx.send(embed = embed)
        if (duration > 0):
            await asyncio.sleep(duration)
            await msg.delete()

bot = CustomBot()

bot.run(Config.get('bot', 'token'))