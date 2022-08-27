import asyncio
import os
import discord

from discord.ext import commands, tasks
from discord import app_commands

from config import get_color, config
from logger import log_info, log_error, log_warning
from message_formatter import make_embed_from_json_file

class GalacticBot(commands.Bot):
    guild_object = discord.Object(id=config['guild']['id'])
    guild = None

    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=config['bot']['prefix'], intents=intents)
        intents.members = True

    async def on_ready(self): 
        self.guild = self.get_current_guild()
        log_info('Bot connected successfully!')
        self.update_activity_loop.start()
        self.update_players_count.start()
    
    @tasks.loop(seconds=60)
    async def update_activity_loop(self):
        messages_part = ['just', 'just type', 'just type !menu']
        for messege in messages_part:
            await asyncio.sleep(3)
            await self.change_presence(activity=discord.Game(name=messege))
            
    @tasks.loop(seconds=360)
    async def update_players_count(self):
        channel = self.get_channel(992029425736626176)
        try:
            players = await self.get_cog('McStats').get_online()
            await channel.edit(name=f'Online: {len(players)}')
        except Exception as e:
            await channel.edit(name=f'Online: ERROR')

    def get_current_guild(self):
        return self.get_guild(config['guild']['id'])

    def get_role(self, id: int):
        return self.guild.get_role(id)

    def get_member(self, id: int):
        return self.guild.get_member(id)

    def get_channel(self, id: int):
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
        #path = os.path.dirname(__file__) + '/modules'
        path = '/home/repositories/python/GalacticManager/src/modules'
        for filename in os.listdir(path):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'modules.{filename[:-3]}')
                log_info(f'{filename[:-3].title()} module has been loaded')
        log_info('All modules has been successfully loaded!')
    
    # MC process events loop
    @tasks.loop(seconds = 1)
    async def mc_events_loop(self):
        cog = self.get_cog('SecurityCog')
        await cog.process_mc_events()

    async def send_json_embed(self, channel: discord.channel = None, message_path: str = None, replace_dict: dict = None, delete_after: int = None, message: discord.message = None, fields = None, view = None):
        '''
        Send Embeded Message from JSON (dict) to discord.channel
        
            message_path - Message path in resources/messages

            replace_dict - Replace <key> on dict['key']

            delete_after - Delete message after N seconds

        Return values:

            discord.message
        '''
        embed = make_embed_from_json_file(message_path, replace_dict)
        if (fields != None):
            for field in fields:
                embed.add_field(name = field.name, value = field.value, inline=field.inline)
        if (message == None):
            return await channel.send(embed = embed, delete_after = delete_after, view = view)
        else:
            return await message.edit(embed = embed, delete_after = delete_after, view = view)

    async def send_simple_embed(self, channel: discord.channel, title: str = None, description: str = None, color: str = None, delete_after: int = None, view = None):
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
        return await channel.send(embed = embed, delete_after = delete_after, view = view)

galactic_bot = GalacticBot()
galactic_bot.run(config['bot']['token'])