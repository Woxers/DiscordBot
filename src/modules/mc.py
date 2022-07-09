import asyncio
import json
import logging
import re

import secrets
import string

from config import Config
from discord.ext import commands

from libs import Database

logger = logging.getLogger(__name__)

class McCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_loop(self):
        return asyncio.get_running_loop()

    async def player_joined(self, nickname):
        print(nickname + ' joined the server')

    async def player_left(self, nickname):
        print(nickname + ' left the server')

    async def player_login(self, nickname):
        id = Database.get_user_id_by_nickname(nickname)[0][0]
        user = self.bot.get_guild(Config.get('guild', 'id')).get_member(id)
        if not Database.check_nickname(nickname):
            pass
            await self.bot.get_cog('MessagesCog').login_mc_server_message(user)
        else:
            print('Пользователь не зарегистрирован через бота!')
        print(nickname + ' logged in')

    async def player_failed_login(self, nickname):
        print(nickname + ' failed login')

    @commands.command(name='setnickname')
    @commands.dm_only()
    async def setnickname(self, ctx, nickname: str):
        if not Database.check_user(ctx.author.id):
            await self.bot.get_cog('MessagesCog').unexpected_error_message(ctx.author)
            return
        
        user = Database.get_user(ctx.author.id)

        if not user['Status'] == 'ACCESS':
            await self.bot.get_cog('MessagesCog').noaccess_error_message(ctx.author)
            return
        
        if not (user['Nickname'] == None or user['Nickname'] == ''):
            await self.bot.get_cog('MessagesCog').already_set_nickname_error_message(ctx.author)
            return

        if not 3 <= len(nickname) <= 16:
            await self.bot.get_cog('MessagesCog').nickname_not_valid_error_message(ctx.author)
            return

        match = re.fullmatch(Config.get('db', 'nickname_pattern'), nickname)
        if not match:
            await self.bot.get_cog('MessagesCog').nickname_not_valid_error_message(ctx.author)
            return

        if not Database.check_nickname(nickname):
            await self.bot.get_cog('MessagesCog').nickname_not_unique_error_message(ctx.author)
            return

        if Database.set_nickname(ctx.author.id, nickname):
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(10))
            print(password + '   ' + nickname)
            if await self.bot.register_player(nickname, password):
                await self.bot.get_cog('MessagesCog').successfully_registered_message(ctx.author, nickname, password)
                await self.bot.get_cog('MessagesCog').new_player_message(ctx.author, nickname)
            else:
                await self.bot.get_cog('MessagesCog').unexpected_error_message(ctx.author)
                Database.set_nickname(ctx.author.id, '')
        else: 
            await self.bot.get_cog('MessagesCog').nickname_not_valid_error_message(ctx.author)
    
    @commands.command(name='online')
    @commands.guild_only()
    async def online(self, ctx):
        if (ctx.channel.id == 992039494616350772):
            online = await self.bot.get_online()
            jsonn = json.loads(online)
            if (not jsonn.get('players_list') is None):
                string = ''
                for players in jsonn['players_list']:
                    if not (players['nickname'] == 'xssluv' or players['nickname'] == 'Woxerss'):
                        string += f"`{players['nickname']}`" + ', '
                        print(players['nickname'])
                if string.endswith(', '):
                    string = string[:-2]
                await self.bot.send_embed(ctx, title=f'Total: {jsonn["total"]}' , description=f'{string}', color='success')
            else:
                await self.bot.send_embed(ctx, description=f'Сервер выключен или перезагружается', color='error')

            
async def setup(bot):
    await bot.add_cog(McCog(bot))