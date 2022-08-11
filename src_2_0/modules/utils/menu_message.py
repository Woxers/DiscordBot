import asyncio
import discord
from discord.ext import commands
from message_formatter import make_embed_from_json_file

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

from discord.ui import Button, View

from database import Database

from .registration_view import RegistrationView

class MenuMessage():
    def __init__(self, bot):
        self.bot = bot                      # Galactic Bot
        
        self.channel = None                 # Channel where to send message
        self.message = None                 # Discord message

        self.color = None                   # Embed color

        self.view = RegistrationView(self)  # Current view

    async def send_menu_message(self):
        fields = []
        embed = make_embed_from_json_file('menu/fields/base_player_field.txt')
        fields.append(embed.fields)
        print(fields)
        try:
            self.auth_message = await self.bot.send_json_embed(self.channel, 'menu/base.txt', view = self.view, fields = fields)
        except Exception as e:
            print(e)