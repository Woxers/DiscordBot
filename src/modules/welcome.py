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

    @commands.command()
    @commands.is_owner()
    async def invites(self, ctx):
        inv = 'Список инвайтов:\n'
        for invite in self.bot.__invites:
            inv += f'{str(invite)[19:]} - Владелец {invite.inviter}\n'
        await ctx.send(inv)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.__invites = await self.bot.get_guild(Config.get('guild', 'id')).invites()
        print("WelcomeCog Listener on ready")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        print(f'New invite {invite.code}')
        self.bot.__invites = await self.bot.get_guild(Config.get('guild', 'id')).invites()
    
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        print(f'Delete invite {invite.code}')
        self.bot.__invites = await self.bot.get_guild(Config.get('guild', 'id')).invites()

    #####################################
    ##           MEMBER JOIN           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'player joined: {member.mention}')

        # Who invited
        invites_before_join = self.bot.__invites
        invites_after_join = await member.guild.invites()
        inviteCode = None
        inviter = None
        for invite in invites_before_join:
            if invite.uses < self.find_invite_by_code(invites_after_join, invite.code).uses:
                inviteCode = invite.code
                inviter = invite.inviter
                self.bot.__invites = invites_after_join
                await self.sendInviterMessage(member, inviter, invite)
                break

        # Addind user to database
        if not (Database.check_user(member.id)):
            if not member.bot:
                print('Заносим нового пользователя в базу')
                Database.add_user(member.id, inviter.id, str(inviteCode))
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
            embed.description = f'Mention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}\n\nInviter: {inviter}\nInvite Code: {inviteCode}'
        embed.set_author(name='User joined!', icon_url=member.avatar_url)
        embed.set_footer(text=f'GS#Total: {member.guild.member_count} \u200b')
        embed.timestamp = datetime.datetime.utcnow()
        await logsChannel.send(embed= embed)

    #####################################
    ##           MEMBER LEFT           ##
    #####################################
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
        await logsChannel.send(embed= embed)
    
    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv

    async def sendInviterMessage(self, member: discord.user, inviter: discord.user, invite: discord.invite):
        embed = discord.Embed(color = Config.getColor('neutral'))
        stroke = ''
        stroke += f'По вашему приглашению `{invite.code}` присоединился новый пользователь. Готовы ли вы за него поручиться? В таком случае игрок пройдет регистрацию в упрощенном формате.'
        stroke += f'\n\n*Пользователь* ID: `{member.id}` - {member.mention}'
        stroke += f'\n\nЧтобы поручиться за пользователя введите: `/confirm ID`'
        embed.description = stroke
        embed.set_footer(text=f'Total Invited: {invite.uses} \u200b')
        embed.title = 'Приглашен игрок!'
        embed.timestamp = datetime.datetime.utcnow()
        await inviter.send(embed = embed)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))