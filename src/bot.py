import discord
import asyncio
import logging

from discord.ext import commands

from libs import Database
from config import Config

class CustomBot(commands.Bot):
    def __init__(self):
        helpCommand = CustomHelpCommand()
        super().__init__(command_prefix=Config.get('bot', 'prefix'), help_command=helpCommand)

    async def on_ready(self): 
        print('Bot connected successfully!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            msg = await ctx.send(embed = discord.Embed(description = f'Command not found', color = int(Config.get('embed', 'accent_color'), 16)))
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
    
    async def command_not_found(self, ctx, *, command=None):
        # Command not found
        print("command_not_found")
        return await super().command_callback(ctx, command=command)

# TODO: Перенести в отдельный файл
class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ping(self, ctx):
        msg = await ctx.send(f'pong in {round(self.bot.latency * 1000)} ms!')
        await asyncio.sleep(5)
        await msg.delete()

    @ping.error
    async def ping_error(self, ctx, error):
        if (str(ctx.channel).startswith("Direct Message with")):
            return
        msg = await ctx.send(embed = discord.Embed(description = f'{error}', color = int(Config.get('embed', 'accent_color'), 16)))
        await asyncio.sleep(5)
        await msg.delete()
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

logging.basicConfig(filename='logs/latest.log',format='%(asctime)s: %(message)s', datefmt='[%y-%m-%d %H:%M:%S]')
logging.warning('Start logging')

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

bot.run(Config.get('bot', 'token'))