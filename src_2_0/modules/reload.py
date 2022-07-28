import asyncio
from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

from database import Database

class ReloadCog(commands.Cog):
    __invites = None

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.__invites = await self.bot.guild.invites()
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

async def setup(bot):
    await bot.add_cog(ReloadCog(bot))