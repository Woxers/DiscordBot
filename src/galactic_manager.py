import os
from tokenize import String
import discord
import asyncio
from os import listdir
import logging
import datetime

from discord.ext import commands
from help import CustomHelpCommand
from config import Config

import log

class CustomBot(commands.Bot):
    __invites = None

    def __init__(self):
        helpCommand = CustomHelpCommand()
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand, intents=intents)
        intents.members = True

    async def setup_hook(self):
        await self.setup_cogs()

    async def on_ready(self): 
        await self.upd_invites()
        print('Bot connected successfully!')

    # Error command not found
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.send_embed(ctx, 'Command not found', None, 3, 'error')

    # Connectins extensions
    async def setup_cogs(self):
        print('Starting load extensions...')
        for filename in listdir('/home/aptem/VScodeRep/DiscordBot/src/modules'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'modules.{filename[:-3]}')
                print(f'Load: {filename[:-3]}')
        print('Done')

    # Sending embeded message
    async def send_embed(self, channel: discord.channel, title = None, description = None, duration: int = None, color = None, footer_text = None, footer_icon = None, author_name = None, author_icon = None, timestamp: bool = None):
        print(f'Sending embeded message in channel {channel}')
        embed = discord.Embed()
        if (title != None):
            embed.title = title
        if (description != None):
            embed.description = description
        if (color != None):
            embed.color = Config.getColor(color)
        if (footer_text != None):
            if (footer_icon != None):
                embed.set_footer(text = footer_text, icon_url= footer_icon)
            else:
                embed.set_footer(text = footer_text)
        if (author_name != None):
            if (author_icon != None):
                embed.set_author(name=author_name, icon_url=author_icon)
            else:
                embed.set_author(name=author_name)
        if (timestamp == True):
            embed.timestamp = datetime.datetime.utcnow()
        
        msg = await channel.send(embed = embed)

        if (duration != None):
            await asyncio.sleep(duration)
            await msg.delete()
    
    # Get all existing invites
    def get_invites(self):
        return self.__invites

    # Update invites list
    async def upd_invites(self):
        self.__invites = await self.get_guild(Config.get('guild', 'id')).invites()

bot = CustomBot()

bot.run(Config.get('bot', 'token'))