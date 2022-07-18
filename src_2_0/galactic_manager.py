import os
import time
import json
import datetime

import discord

from sys import platform

from discord.ext import commands
from config import get_color, config
from logger import log_info, log_error
from message_formatter import make_embed_from_json_file

class GalacticBot(commands.Bot):
    guild = None

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=config['bot']['prefix'], intents=intents)
        intents.members = True

    async def on_ready(self): 
        self.guild = self.get_current_guild()
        log_info('Bot connected successfully!')
    
    def get_current_guild(self):
        return self.get_guild(config['guild']['id'])

    def get_role_by_id(self, id: int):
        return self.guild.get_role(id)

    def get_member_by_id(self, id: int):
        return self.guild.get_member(id)

    def get_channel_by_id(self, id: int):
        return self.guild.get_channel(id)

    # Error command not found
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.send_simple_embed(ctx, None, 'Command not found', 'error')
    
    # What to do in setup
    async def setup_hook(self):
        await self.setup_cogs()

    # Connectins extensions
    async def setup_cogs(self):
        '''Setup all modules'''
        path = os.path.dirname(__file__) + '/modules'
        for filename in os.listdir(path):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'modules.{filename[:-3]}')
                log_info(f'{filename[:-3].title()} module has been loaded')
        log_info('All modules has been successfully loaded!')

    async def send_json_embed(self, channel: discord.channel, message_path: str, replace_dict: dict = None, delete_after: int = None):
        '''
        Send Embeded Message from JSON (dict) to discord.channel
        
            message_path - Message path in resources/messages

            replace_dict - Replace <key> on dict['key']

            delete_after - Delete message after N seconds

        Return values:

            discord.message
        '''
        embed = make_embed_from_json_file(message_path, replace_dict)
        return await channel.send(embed = embed, delete_after = delete_after)

    async def send_simple_embed(self, channel: discord.channel, title: str = None, description: str = None, color: str = None, delete_after: int = None):
        '''
        Send Embeded Message to discord.channel
        
            color - 'neutral', 'success', 'error

            delete_after - Delete message after N seconds

        Return values:

            discord.message
        '''
        embed = discord.Embed()
        if (title != None):
            embed.title = title
        if (description != None):
            embed.description = description
        if (color != None):
            embed.color = get_color(color)
        a = embed.to_dict()
        return await channel.send(embed = embed, delete_after = delete_after)
        
galactic_bot = GalacticBot()
galactic_bot.run(config['bot']['token'])