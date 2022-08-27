import discord

from mcstatus import JavaServer

from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
from config import get_color, config

class McStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("McStats Module successfully loaded!")

    @commands.command(name='online')
    async def online_command(self, ctx, *args):
        server = JavaServer.lookup(config['mc_server']['ip'])
        status = server.status()
        
        online_count = status.players.online
        latency = status.latency
        
        # Online count string
        online = ''
        if (online_count == 0):
            online = f'{online_count} игроков'
        elif (online_count == 1):
            online = f'{online_count} игрок'
        elif (online_count > 1 and online_count < 5):
            online = f'{online_count} игрока'
        else:
            online = f'{online_count} игроков'
            
        embed = discord.Embed()
        embed.title = 'Онлайн на сервере'
        embed.add_field(name='Всего', value=online, inline=True)
        embed.add_field(name='Пинг', value=f'{latency:.2f} мс', inline=True)
        
        embed.color = get_color('neutral')

        query = server.query()
        players = query.players.names
        players_string = None
        if (len(players) > 0):
            players_string = '`' + '`, `'.join(players) + '`'
        
        if (players_string != None):
            embed.add_field(name='Список игроков', value=players_string, inline=False)
            
        await ctx.send(embed=embed)
        
    async def get_online(self) -> list:
        server = JavaServer.lookup(config['mc_server']['ip'])
        query = server.query()
        return query.players.names
    
async def setup(bot):
    await bot.add_cog(McStats(bot))