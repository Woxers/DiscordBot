import asyncio
from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

from database import Database

class ReloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("Reload Module successfully loaded!")

    @commands.command()
    @commands.is_owner() 
    async def reload(self, ctx, *args):
        extensions = list()
        for extension in self.bot.extensions:
            if not (extension == 'modules.reload'): 
                extensions.append(extension)
        for extension in extensions:
            await self.bot.unload_extension(extension)
            await self.bot.load_extension(extension)
        log_warning('All extensions are reloaded!')
        await self.bot.send_simple_embed(ctx.channel, title='Команда выполнена', description='Все модули были перезагружены!', color='success')

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ping(self, ctx):
        await self.bot.send_simple_embed(ctx.channel, title='Ping', description=f'pong in {round(self.bot.latency * 1000)} ms!', color='success', delete_after= 5)

    @ping.error
    async def ping_error(self, ctx, error):
        if (str(ctx.channel).startswith("Direct Message with")):
            return
        await self.bot.send_simple_embed(ctx.channel, title='Error', description=f'{error}', color='error', delete_after= 5)

async def setup(bot):
    await bot.add_cog(ReloadCog(bot))