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
from sys import platform

import log

class CustomBot(commands.Bot):
    __invites = None

    def __init__(self):
        helpCommand = CustomHelpCommand()
        intents = discord.Intents.all()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand, intents=intents)
        intents.members = True
        self.setupCogs()

    async def on_ready(self): 
        await self.upd_invites()
        print('Bot connected successfully!')

    # Ошибка команда не найдена
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.sendEmbed(ctx, 'Command not found', None, 3, 'error')

    # Подключаем модули
    def setupCogs(self):
        for filename in listdir('/home/aptem/VScodeRep/DiscordBot/src/modules'):
            if filename.endswith('.py') and not filename.startswith('__'):
                self.load_extension(f'modules.{filename[:-3]}')
                print(f'load: {filename[:-3]}')
            else:
                print(f'Unable to load {filename[:-3]}')

    # Функция отправки embed сообщения
    async def sendEmbed(self, channel: discord.channel, title = None, description = None, duration: int = None, color = None, footer_text = None, footer_icon = None, author_name = None, author_icon = None, timestamp: bool = None):
        print('send embed')
        embed = discord.Embed()
        if (title != None):
            embed.title = title
        if (description != None):
            embed.description = description
        if (color != None):
            embed.color = Config.getColor(color)
        if (footer_text != None) or (footer_icon != None):
            embed.set_footer(text = footer_text, icon_url= footer_icon)
        if (author_name != None or author_icon != None):
            embed.set_author(name=author_name, icon_url=author_icon)
        if (timestamp == True):
            embed.timestamp = datetime.datetime.utcnow()
        
        msg = await channel.send(embed = embed)

        if (duration != None):
            await asyncio.sleep(duration)
            await msg.delete()
    
    # Поулчить существующие инвайты
    def get_invites(self):
        return self.__invites

    # Обновить список инвайтов
    async def upd_invites(self):
        self.__invites = await self.get_guild(Config.get('guild', 'id')).invites()
        

bot = CustomBot()

bot.run(Config.get('bot', 'token'))