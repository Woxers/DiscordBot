import logging

from config import Config
from discord.ext import commands

logger = logging.getLogger(__name__)

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload')
    @commands.is_owner()
    async def reload(self, ctx):
        extensions = list()
        for extension in self.bot.extensions:
            if not (extension == 'modules.owner'): extensions.append(extension)
        for extension in extensions:
            if not (extension == 'modules.owner'):
                self.bot.unload_extension(extension)
                self.bot.load_extension(extension)
        print('reloaded')
        logger.warning('All extensions are reloaded!')
        await self.bot.sendEmbed(ctx, 'Command executed', 'All extensions are reloaded!', '0', 'success')

def setup(bot):
    bot.add_cog(OwnerCog(bot))