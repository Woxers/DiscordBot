import os
import time
import json
import datetime

import discord

from sys import platform

from discord.ext import commands
from config import get_color, config
from logger import log_info, log_error

class GalacticBot(commands.Bot):
    guild: discord.guild = None

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=config['bot']['prefix'], intents=intents)
        intents.members = True

    async def on_ready(self): 
        self.guild = self.get_guild(config['guild']['id'])
        log_info('Bot connected successfully!')
    
    # Setup modules
    async def setup_hook(self):
        await self.setup_cogs()

    # Connectins extensions
    async def setup_cogs(self):
        path = os.path.dirname(__file__) + '\modules'
        for filename in os.listdir(path):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'modules.{filename[:-3]}')
                print(f'Load: {filename[:-3]}')
        print('Done')

    # Error command not found
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed()
            await self.send_simple_embed(ctx, None, 'Command not found', 'error')

    # Send embed from dict
    async def send_json_embed(self, channel: discord.channel, embed_dict: dict, replace_dict: dict = None, delete_after: int = None):
        if (not replace_dict == None):
            json_string = json.dumps(embed_dict)
            json_string = json.format(**replace_dict)
            embed_dict = json.loads(json_string)
        embed = discord.Embed.from_dict(dict)
        return await channel.send(embed = embed)

    # Send simple embed
    async def send_simple_embed(self, channel: discord.channel, title: str = None, description: str = None, color: str = None, duration: int = None):
        embed = discord.Embed()
        if (title != None):
            embed.title = title
        if (description != None):
            embed.description = description
        if (color != None):
            embed.color = get_color(color)
        a = embed.to_dict()
        return await channel.send(embed = embed, delete_after = duration)

    # Send embed message
    async def send_embed(self, channel: discord.channel, title = None, description = None, duration: int = None, color = None, footer_text = None, footer_icon = None, author_name = None, author_icon = None, timestamp: bool = None, view = None):
        print(f'Sending embeded message in channel {channel}')
        embed = discord.Embed()
        if (title != None):
            embed.title = title
        if (description != None):
            embed.description = description
        if (color != None):
            embed.color = color(color)
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
        
        return await channel.send(embed = embed, view = view, delete_after = duration)

galactic_bot = GalacticBot()
galactic_bot.run(config['bot']['token'])