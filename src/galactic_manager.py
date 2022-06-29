import os
import time
import json
import datetime

import discord

import asyncio
import threading

import requests
import urllib3

from discord.ext import tasks 

from os import listdir

from help import CustomHelpCommand
from discord.ext import commands
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
    async def receive_mc_events(cls):
        try:
            r = requests.get(f'{cls.url}events', verify=False, data={"token":cls.token})
            jsonn = json.loads(r.text)
            if 'events' not in jsonn:
                raise Exception(f'Reply doesnt contains events: \n {jsonn}')
            for event in jsonn['events']:
                if event['type'] == 'player_joined':
                    await cls.handle_events(cls.__joined_event_handlers, event['value'])
                elif event['type'] == 'player_quit':
                    await cls.handle_events(cls.__left_event_handlers, event['value'])
                elif event['type'] == 'player_login':
                    await cls.handle_events(cls.__login_event_handlers, event['value'])
                elif event['type'] == 'player_failed_login':
                    await cls.handle_events(cls.__failed_login_event_handlers, event['value'])
            time.sleep(0.5)
        except Exception as e:
            print(e)
            time.sleep(2)
            pass
    
    # Register player
    @classmethod
    def register_player(cls, nickname, password):
        r = requests.get(f'{cls.url}register', verify=False, data={"token":cls.token, "nickname":nickname, "password": password})
        if r.status_code == 501 or r.status_code == 401:
            print(r.content)
            return 0
        return 1

    # Unregister player
    @classmethod
    def unregister_player(cls, nickname):
        try:
            r = requests.get(f'{cls.url}unregister', verify=False, data={"token":cls.token, "nickname":nickname})
            print(r)
            if r.status_code == 501 or r.status_code == 401:
                raise Exception(r.content);
        except Exception as e:
            log.info(e)
            print(e)
            pass
            return 0
        return 1
    
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
    __last_deleted_inviter = None

    def __init__(self):
        helpCommand = CustomHelpCommand()
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand, intents=intents)
        intents.members = True

    @tasks.loop(seconds = 1)
    async def mc_receive_message_loop(self):
        await self.client.receive_mc_events()

    async def setup_hook(self):
        await self.setup_cogs()

    async def on_ready(self): 
        await self.upd_invites()
        self.mc_receive_message_loop.start()
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

    async def send_embed_from_json(self, path):
        pass

    # Sending embeded message
    async def send_embed(self, channel: discord.channel, title = None, description = None, duration: int = None, color = None, footer_text = None, footer_icon = None, author_name = None, author_icon = None, timestamp: bool = None, view = None):
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
        
        return await channel.send(embed = embed, view = view, delete_after = duration)

    # Get all existing invites
    def get_invites(self):
        return self.__invites

    # Update invites list
    async def upd_invites(self):
        self.__invites = await self.get_guild(Config.get('guild', 'id')).invites()

    @client.listener
    async def on_player_join(name):
        await bot.get_cog('McCog').player_joined(name)

    @client.listener
    async def on_player_left(name):
        await bot.get_cog('McCog').player_left(name)

    @client.listener
    async def on_player_login(name):
        await bot.get_cog('McCog').player_login(name)

    @client.listener
    async def on_player_failed_login(name):
        await bot.get_cog('McCog').player_failed_login(name)

    async def register_player(self, nickname, password):
        return self.client.register_player(nickname, password)

    async def unregister_player(self, nickname, password):
        return self.client.unregister_player(nickname)

bot = CustomBot()

bot.run(Config.get('bot', 'token'))