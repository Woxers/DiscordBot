import discord
from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

from .utils.database.players_db import PlayersDatabase

class OwnerCog(commands.Cog):
    __invites = None

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.__invites = await self.bot.guild.invites()
        log_info("Owner Module successfully loaded!")

    @commands.command(name='compare-with-db')
    @commands.is_owner() 
    async def check_all_users(self, ctx, *args):
        for id in PlayersDatabase.execute_query('SELECT id FROM discord'):
            mem = self.bot.guild.get_member(id[0])
            if(mem == None):
                log_warning(f'Member with id: {id[0]} in database, but not on server')
                if (PlayersDatabase.get_user_by_id(id[0])['status'] == 'access'):
                    PlayersDatabase.set_status_by_user_id(id[0], 'lost_access')
                    log_warning(f'\t> He had access to mc!')
                    await ctx.send(f'<@{id[0]}> мышь!')
        await self.bot.send_simple_embed(ctx.channel, title='Команда выполнена', description='Все участники гильдии соотнесены с базой!', color='success')

    @commands.command(name='get-not-registered')
    @commands.is_owner() 
    async def get_not_reg(self, ctx, *args):
        dt_ex = {}
        dt_not = {}
        for status in PlayersDatabase.execute_query('SELECT name FROM statuses'):
            _status = status[0].lower()
            dt_ex[_status] = []
            dt_not[_status] = []
        for id in PlayersDatabase.execute_query('SELECT id FROM discord'):
            _id = id[0]
            db_user = PlayersDatabase.get_user_by_id(_id)
            players = PlayersDatabase.get_players_by_id(_id)
            if (players == {}):
                try:
                    if (self.bot.guild.get_member(_id) == None):
                        print('no: ' + str(_id))
                        dt_not[db_user['status']].append(str(_id))
                    else:
                        print('ex: ' + str(_id))
                        dt_ex[db_user['status']].append(f'<@{str(_id)}>')
                except Exception as e:
                    print(e)
        print('done')
        embed = discord.Embed()
        embed.title = 'Not registered that now on server'
        embed.color = get_color('success')
        for key in dt_ex:
            if (len(dt_ex[key]) > 0):
                embed.add_field(name=f'{key}', value=f"\n".join(dt_ex[key]), inline=1)
        await ctx.send(embed=embed)

        embed = discord.Embed()
        embed.title = 'Not registered that left from server'
        embed.color = get_color('error')
        for key in dt_not:
            if (len(dt_not[key]) > 0):
                embed.add_field(name=f'{key}', value=f"\n".join(dt_not[key]), inline=1)
        await ctx.send(embed=embed)

    @commands.command(name='not-reg-to-verified')
    @commands.is_owner() 
    async def not_reg_to_verified(self, ctx, *args):
        try:
            access_role = self.bot.guild.get_role(config['roles']['access'])
            verified_role = self.bot.guild.get_role(config['roles']['verified'])

            for member in self.bot.guild.members:
                if (not member.bot):
                    if (PlayersDatabase.get_players_by_id(member.id) == {}):
                        db_user = PlayersDatabase.get_user_by_id(member.id)
                        if (db_user['status'] == 'access'):
                            if access_role in member.roles:
                                await member.remove_roles(access_role)
                            await member.add_roles(verified_role)
                            PlayersDatabase.set_status_by_user_id(member.id, 'verified')
                            print(member.mention)
            await self.bot.send_simple_embed(ctx.channel, title='Команда выполнена', description='Незарегистрированные участники теперь просто verified!', color='success')
        except Exception as e:
            print(e)

    @commands.command(name='add-to-db')
    @commands.is_owner() 
    async def add_to_db(self, ctx, *args):
        try:
            for member in self.bot.guild.members:
                if (not PlayersDatabase.ckeck_user(member.id)):
                    print(member.id)
        except Exception as e:
            print(e)

    @commands.command(name='get-users-compared-to-players')
    @commands.is_owner() 
    async def get_user_compared_to_players(self, ctx, *args):
        try:
            string = '```'
            for member in self.bot.guild.members:
                if (not member.bot):
                    db_user = PlayersDatabase.get_user_by_id(member.id)
                    if db_user['status'] == 'access':
                        string += member.name + f'\t=>\t' + ", ".join(PlayersDatabase.get_players_by_id(member.id)) + f'\n'
            string += '```'
            await ctx.send(string)
            print('Done!')
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(OwnerCog(bot))