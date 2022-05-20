import discord
import asyncio

from discord.ext import commands

from libs import Database
from config import bot_settings, db_settings, embed_settings

class CustomBot(commands.Bot):
    def __init__(self):
        helpCommand = CustomHelpCommand()
        super().__init__(command_prefix=bot_settings['prefix'], help_command=helpCommand)

    async def on_ready(self): 
        print('Bot connected successfully!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            msg = await ctx.send(embed = discord.Embed(description = f'Command not found', color = embed_settings['accent_color']))
            await asyncio.sleep(3)
            await msg.delete()

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
    
    async def command_not_find(self, ctx, *, command=None):
        print("command_not_find")
        return await super().command_callback(ctx, command=command)

# TODO: Перенести в отдельный файл
class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ping(self, ctx):
        msg = await ctx.send(f'pong in {round(self.bot.latency * 1000)} ms!')
        await asyncio.sleep(5)
        await msg.delete()

    @ping.error
    async def ping_error(self, ctx, error):
        msg = await ctx.send(embed = discord.Embed(description = f'{error}', color = embed_settings['accent_color']))
        await asyncio.sleep(5)
        await msg.delete()

# TODO: Перенести в отдельный файл
def setupUtilityCog(CustomBot):
    bot.add_cog(UtilityCog(bot))

bot = CustomBot()
setupUtilityCog(bot)

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         msg = await ctx.send(embed = discord.Embed(description = f'Command not found', color = embed_setting['accent_color']))
#         await asyncio.sleep(3)
#         await msg.delete()

bot.run(bot_settings['token'])