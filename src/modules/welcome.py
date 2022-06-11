import datetime
from pydoc import describe
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
        await self.bot.upd_invites()
        print("WelcomeCog Listener on ready")

    # Ивент создание инвайта
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        print(f'New invite {invite.code}')
        await self.bot.upd_invites()
    
    # Событие удаление инвайта
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        print(f'Delete invite {invite.code}')
        await self.bot.upd_invites()

    #####################################
    ##           MEMBER JOIN           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'Player joined: {member.mention}')

        # Who invited
        invites_before_join = self.bot.get_invites()
        invites_after_join = await member.guild.invites()
        inviteCode = None
        inviter = None
        for invite in invites_before_join:
            if invite.uses < self.find_invite_by_code(invites_after_join, invite.code).uses:
                inviteCode = invite.code
                inviter = invite.inviter
                await self.bot.upd_invites()
                break

        # Addind user to database
        if not (Database.check_user(member.id)):
            newbie = '***NEWBIE***\n'
            if not member.bot:
                print('Adding new player to database')
                Database.add_user(member.id, inviter.id, str(inviteCode))
                await self.send_invite_message(member, inviter, invite)
                await self.bot.get_cog('VerificationCog').new_unconfirmed_player(member)
        else:
            newbie = '**OLD PLAYER**\n'
            print('Player is not newbie')

        # Adding auto-role
        if (Config.get('role', 'enabled')):
            roleId = Config.get('role', 'id')
            role = discord.utils.get(member.guild.roles, id=roleId)
            await member.add_roles(role, reason='Auto-role')

        # Message to log channel
        if not (Config.get('greetings', 'enabled')):
            return
        logsChannel = self.bot.get_channel(Config.get('greetings', 'id'))
        if (member.bot):
            await self.bot.send_embed(logsChannel, description=f'Welcome {member.mention}, brother' , color='neutral')
        else:
            created = member.created_at
            created = created.strftime('%Y-%m-%d')
            description = f'{newbie}Mention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}\n\nInviter: {inviter.mention}\nInvite Code: {inviteCode}'
            footer_text=f'GS#Total: {member.guild.member_count} \u200b'
            await self.bot.send_embed(logsChannel, color='success', description=description, author_icon=member.avatar_url, author_name='User joined!', footer_text=footer_text, timestamp=True)

    #####################################
    ##           MEMBER LEFT           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'Player left: {member.mention}')

        # Message to log channel
        if not (Config.get('greetings', 'enabled')):
            return
        logsChannel = self.bot.get_channel(Config.get('greetings', 'id'))
        embed = discord.Embed(color = Config.getColor('error'))
        if (member.bot):
            await self.bot.send_embed(logsChannel, description=f'Goodbye {member.mention}, brother' , color='neutral')
        else:
            created = member.created_at
            created = created.strftime('%Y-%m-%d')
            description = f'Mention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}'
            footer_text=f'GS#Total: {member.guild.member_count} \u200b'
            await self.bot.send_embed(logsChannel, color='success', description=description, author_icon=member.avatar_url, author_name='User left!', footer_text=footer_text, timestamp=True)

    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv

    async def send_invite_message(self, member: discord.user, inviter: discord.user, invite: discord.invite):
        embed = discord.Embed(color = Config.getColor('neutral'))
        stroke = ''
        stroke += f'По вашему приглашению `{invite.code}` присоединился новый пользователь. Готовы ли вы за него поручиться? В таком случае игрок пройдет регистрацию в упрощенном формате.'
        stroke += f'\n\n*Пользователь* ID: `{member.id}` - {member.mention}'
        stroke += f'\n\nЧтобы поручиться за пользователя введите: `!confirm ID`'
        embed.description = stroke
        embed.set_footer(text=f'Total Invited: {invite.uses} \u200b')
        embed.title = 'Приглашен игрок!'
        embed.timestamp = datetime.datetime.utcnow()
        await inviter.send(embed = embed)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))