import logging

from config import Config
from discord.ext import commands

from libs import Database

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
        await self.bot.send_embed(ctx.channel, title='Command executed', description='All extensions are reloaded!', color='success')

    @commands.command(name='upd-players')
    @commands.is_owner()
    async def update_users_db(self, ctx):
        print('works')
        stroke = 'Добавлены в базу:\n'
        guild = self.bot.get_guild(Config.get('guild', 'id'))
        for member in guild.members:
            if not (member.bot):
                print(member.id)
                if not (Database.check_user(member.id)):
                    print('Заносим нового пользователя в базу')
                    stroke += f'{member}\n'
                    Database.add_user(member.id, 222746438814138368)
                    Database.set_stage(member.id, 'CHECKED')
                    Database.set_status(member.id, 'CONFIRMED')
                    Database.set_confirmator(member.id, 222746438814138368)
                    logger.info(f'Added new player to database: {member.id}')
        await ctx.send(stroke)
    
    @commands.command(name='upd-joined-date')
    @commands.is_owner()
    async def update_joined_time(self, ctx):
        print('works')
        guild = self.bot.get_guild(Config.get('guild', 'id'))
        for member in guild.members:
            if not (member.bot):
                print('Update joined datetime')
                Database.upd_joined_date(member.id, member.joined_at)
        await ctx.send('DONE')

def setup(bot):
    bot.add_cog(OwnerCog(bot))