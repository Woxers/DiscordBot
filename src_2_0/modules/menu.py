import re
import discord

from discord.ext import commands

from logger import log_error, log_info
from .utils.user import GalacticUser

from .utils.database.players_db import PlayersDatabase
from .utils.menu_message import NewMenuMessage

from .utils.mc_skins import SkinProvider

class MenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.menu_messages = {}

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("Menu Module successfully loaded!")

    @commands.hybrid_command(name='head')
    async def head_command(self, ctx, username:str = None):
        username = username.lower()
        if (PlayersDatabase.authme_check_nickname(username)):
            with open(SkinProvider.get_head(username), 'rb') as head_image:
                picture = discord.File(head_image)
                await ctx.send(file=picture)
        else:
            raise ValueError(f'Такого игрока нет на сервере: {username}')

    @head_command.error
    async def head_command_error(self, ctx, error):
        await ctx.send(f'Ошибка: {error}')

    @commands.hybrid_command(name='test_1')
    @commands.is_owner() 
    async def test_command(self, ctx, mem:str = None):
        if (mem == None):
            mem = ctx.author
        else:
            nums = re.findall(r'\b\d+\b', mem)
            print(nums)
            try:
                mem = self.bot.get_member(int(nums[0]))
            except Exception as e:
                print(e)
                ctx.send('Error')
        print(type(mem))
        galactic_user = GalacticUser(self.bot.get_member(mem.id))
        try:
            string = ''
            string += f'user: {galactic_user.user.mention}\n'
            string += f'inviter: <@{galactic_user.inviter_id}>\n'
            string += f'\n'
            string += f'invited_players: {galactic_user.invited_players}\n'
            string += f'invited_users: {galactic_user.invited}\n'
            string += f'\n'
            string += f'status: {galactic_user.status.name}\n'
            string += f'icon: {galactic_user.status.value["emoji"]}\n'
            string += f'name: {galactic_user.status.value["name"]}\n'
            string += f'description: {galactic_user.status.value["description"]}\n'
            string += f'\n'
            for players in galactic_user.players:
                string += f'**{players.realname}**\n'
                string += f'last_ip: {players.last_ip}\n'
                string += f'last_login: {players.last_login.strftime("%Y-%m-%d %H:%M")}\n'
                string += f'reg_date: {players.reg_date.strftime("%Y-%m-%d %H:%M")}\n'
                string += f'is_logged: {players.is_logged}\n'
                string += f'has_access: {players.has_access}\n'
                string += f'*groups:* \n'
                for group in players.groups:
                    string += f'group: `{group.name} {group.value["emoji"]} {group.value["weight"]} {group.value["primary"]}`\n'
                string += f'settings: quick_auth({players.settings["quick_auth_enabled"]}) join_notify({players.settings["join_notify_enabled"]})\n'
            await ctx.send(string)
        except Exception as e:
            print(e)

    @commands.hybrid_command(name='menu')
    @commands.is_owner()
    async def menu_command(self, ctx):
        try:
            # Close opened user's menu if exist
            if str(ctx.author.id) in self.menu_messages.keys():
                await self.menu_messages[str(ctx.author.id)].close('another menu openned')
            # Open new menu
            menu_message = await NewMenuMessage.create(self.bot, ctx.author, ctx.channel)
            self.menu_messages[str(ctx.author.id)] = menu_message
        except Exception as e:
            log_error(e)
            raise(e)
    
    @menu_command.error
    async def menu_command_error(self, ctx, error):
        await self.bot.send_simple_embed(ctx.channel, title='Непредвиденная ошибка!', description=f'Пожалуйста, обратитесь к администратору <@222746438814138368>, чтобы решить эту проблему.', color='error')

async def setup(bot):
    await bot.add_cog(MenuCog(bot))