import discord
import asyncio
import logging

from config import Config
from discord.ext import commands

logger = logging.getLogger(__name__)

# TODO: Перенести в отдельный файл
class CustomHelpCommand(commands.HelpCommand):
    helpPages = [['Utility', '- ping\n- hello\n- hi @someone'], ['Test', '- ping\n- hello\n- hi @someone']]

    async def send_bot_help(self, mapping):
        # Embed generator for python:
        # https://cog-creators.github.io/discord-embed-sandbox/
        destination = self.get_destination()
        embededMessage = discord.Embed(title='Help Command')
        for page in self.helpPages:
            embededMessage.add_field(name=page[0], value=page[1])
        await destination.send(embed=embededMessage)
        return await super().send_bot_help(mapping)
    
    async def command_not_found(self, ctx, *, command=None):
        # Command not found
        print("command_not_found")
        return await super().command_callback(ctx, command=command)