import datetime
import discord
import logging

from config import Config
from libs import Database
from discord.ext import commands

logger = logging.getLogger(__name__)

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        logger.info('Connecting Welcome module')

    @commands.Cog.listener()
    async def on_ready(self):
        print("WelcomeCog Listener on ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'player joined: {member.mention}')

        # Addind user to database
        if not (Database.check_user(member.id)):
            if not member.bot:
                Database.add_user(member.id)
                logger.info(f'Added new player to database: {member.id}')

        # Adding auto-role
        if (Config.get('role', 'enabled')):
            roleId = Config.get('role', 'id')
            role = discord.utils.get(member.guild.roles, id=roleId)
            await member.add_roles(role, reason='Auto-role')

        # Message to log channel
        if not (Config.get('greetings', 'enabled')):
            return
        logsChannel = self.bot.get_channel(Config.get('greetings', 'id'))
        embed = discord.Embed(color = Config.getColor('success'))
        if (member.bot):
            embed.description = f'Welcome {member.mention}, brother'
        else:
            created = member.created_at
            created = created.strftime('%Y-%m-%d')
            embed.description = f'Mention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}'
        embed.set_author(name='User joined!', icon_url=member.avatar_url)
        embed.set_footer(text=f'GS#Total: {member.guild.member_count} \u200b')
        embed.timestamp = datetime.datetime.utcnow()
        await logsChannel.send(embed= embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'player left: {member.mention}')

        # Message to log channel
        if not (Config.get('greetings', 'enabled')):
            return
        logsChannel = self.bot.get_channel(Config.get('greetings', 'id'))
        embed = discord.Embed(color = Config.getColor('error'))
        if (member.bot):
            embed.description = f'Goodbye {member.mention}, brother'
        else:
            created = member.created_at
            created = created.strftime('%Y-%m-%d')
            embed.description = f'Mention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}'
        embed.set_author(name='User left!', icon_url=member.avatar_url)
        embed.set_footer(text=f'GS#Total: {member.guild.member_count} \u200b')
        embed.timestamp = datetime.datetime.utcnow()
        print('send')
        await logsChannel.send(embed= embed)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))