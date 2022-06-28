import json
import os
import threading
import time
from tokenize import String
import discord
import asyncio
from os import listdir
import datetime

from discord.ext import commands
import requests
import urllib3
from help import CustomHelpCommand
from config import Config

import log

# Singleton
class McApiClient:
    urllib3.disable_warnings()

    host = Config.get('server', 'host')
    port = Config.get('server', 'port')
    token = Config.get('server', 'token')

    url = 'https://' + host + ':' + port + '/'

    __instance = None
    __joined_event_handlers = []
    __left_event_handlers = []
    __login_event_handlers = []
    __failed_login_event_handlers = []

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(McApiClient, cls).__new__(cls)
        return cls.__instance
    
    # Start receiving events
    @classmethod
    def start(cls): 
        _thread = threading.Thread(target=cls.receive_mc_events)
        _thread.start()

    # Receive events
    @classmethod
    def receive_mc_events(cls):
        print(f'\nMC receiving events started!')
        while(True):
            try:
                r = requests.get(f'{cls.url}events', verify=False, data={"token":cls.token})
                jsonn = json.loads(r.text)
                if 'events' not in jsonn:
                    raise Exception(f'Reply doesnt contains events: \n {jsonn}')
                for event in jsonn['events']:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    if event['type'] == 'player_joined':
                        loop.run_until_complete(cls.handle_events(cls.__joined_event_handlers, event['value']))
                    elif event['type'] == 'player_quit':
                        loop.run_until_complete(cls.handle_events(cls.__left_event_handlers, event['value']))
                    elif event['type'] == 'player_login':
                        loop.run_until_complete(cls.handle_events(cls.__login_event_handlers, event['value']))
                    elif event['type'] == 'player_failed_login':
                        loop.run_until_complete(cls.handle_events(cls.__failed_login_event_handlers, event['value']))
                    loop.close
                time.sleep(0.5)
            except Exception as e:
                print(e)
                time.sleep(2)
                pass
    
    # Handle received events
    @classmethod
    async def handle_events(cls, handlers, value):
        for handler in handlers:
            await handler(value)

    # Listener Decorator
    @classmethod
    def listener(cls, event_handler):
        def wrapper():
            if (event_handler.__name__ == 'on_player_join'):
                cls.__joined_event_handlers.append(event_handler)
            elif (event_handler.__name__ == 'on_player_left'):
                cls.__left_event_handlers.append(event_handler)
            elif (event_handler.__name__ == 'on_player_login'):
                cls.__login_event_handlers.append(event_handler)
            elif (event_handler.__name__ == 'on_player_failed_login'):
                cls.__failed_login_event_handlers.append(event_handler)
            else:
                raise Exception(f'Undefined event listener \"{event_handler.__name__}\"')
        return wrapper()

class CustomBot(commands.Bot):
    client = McApiClient()
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
        self.client.start()
        print('Bot connected successfully!')

    # Error command not found
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.send_embed(ctx, 'Command not found', None, 3, 'error')

    # Connectins extensions
    async def setup_cogs(self):
        print('Starting load extensions...')
        for filename in listdir(os.getcwdb().decode("utf-8") + '\modules'):
        #for filename in listdir('/home/aptem/VScodeRep/DiscordBot/src/modules'):
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

    @client.listener
    async def on_player_join(name):
        print(name + ' joined the server')

    @client.listener
    async def on_player_left(name):
        print(name + ' left the server')

    @client.listener
    async def on_player_login(name):
        print(name + ' logged in')

    @client.listener
    async def on_player_failed_login(name):
        print(name + ' failed login')

bot = CustomBot()

bot.run(Config.get('bot', 'token'))