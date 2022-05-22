import discord
import asyncio

from config import Config
from discord.ext import commands

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