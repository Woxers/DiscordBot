from copy import deepcopy
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

        try:
            for invite in invites_before_join:
                if invite.uses < self.find_invite_by_code(invites_after_join, invite.code).uses:
                    inviteCode = invite.code
                    inviter = invite.inviter
                    await self.bot.upd_invites()
                    break
        except Exception as e:
            pass

        if (inviter == None):
            inviteCode = 'error'
            inviter = self.bot.get_user(222746438814138368)
            await self.bot.upd_invites()

        joinedStatus = ''
        # Is user in database?
        if not Database.check_user(member.id):
            isNewbie = True
            if not member.bot:
                joinedStatus = 'NEWBIE'
                print('Adding new player to database')
                Database.add_user(member.id, inviter.id)
                role = discord.utils.get(member.guild.roles, id=Config.get('role', 'candidate'))
                await member.add_roles(role, reason='Newbie Auto-role')
                await self.bot.get_cog('MessagesCog').send_inviter_message(member, inviter, invite)
                await self.bot.get_cog('MessagesCog').send_newbie_message_on_join(member)
        else:
            verification = Database.get_status_and_stage(member.id)
            if (verification['status'] == 'JOINED'):
                print('Зашедший пользователь ранее не прошел верификацию до конца')
                joinedStatus = 'NOT VERIFIED IN PAST'
                Database.delete_user(member.id)
                print('Adding new player to database')
                Database.add_user(member.id, inviter.id)
                role = discord.utils.get(member.guild.roles, id=Config.get('role', 'candidate'))
                await member.add_roles(role, reason='Newbie Auto-role')
                await self.bot.get_cog('MessagesCog').send_inviter_message(member, inviter, invite)
                await self.bot.get_cog('MessagesCog').send_newbie_message_on_join(member)
            elif(verification['status'] == 'REJECTED'):
                joinedStatus = 'REJECTED'
                print('Зашедший пользователь ранее был отклонен по время верификации')
                role = discord.utils.get(member.guild.roles, id=Config.get('role', 'rejected'))
                await member.add_roles(role, reason='Rejected Auto-role')
                await self.bot.get_cog('MessagesCog').send_rejected_message_on_join(member)
            elif(verification['status'] == 'SPECTATOR'):
                joinedStatus = 'SPECTATOR'
                print('Зашедший пользователь ранее был спектатором')
                role = discord.utils.get(member.guild.roles, id=Config.get('role', 'spectator'))
                await member.add_roles(role, reason='Spectator Auto-role')
                await self.bot.get_cog('MessagesCog').send_spectator_message_on_join(member)
            elif(verification['status'] == 'ACCESS'):
                joinedStatus = 'HAD ACCESS'
                print('Зашедший пользователь ранее имел доступ к minecraft серверу')
                Database.set_status(member.id, 'CONFIRMED')
                role = discord.utils.get(member.guild.roles, id=Config.get('role', 'verified'))
                await member.add_roles(role, reason='Verified Auto-role')
                await self.bot.get_cog('MessagesCog').send_access_message_on_join(member)
            elif(verification['status'] == 'CONFIRMED'):
                joinedStatus = 'VERIFIED'
                print('Зашедший пользователь ранее верифицирован')
                role = discord.utils.get(member.guild.roles, id=Config.get('role', 'verified'))
                await member.add_roles(role, reason='Verified Auto-role')
                await self.bot.get_cog('MessagesCog').send_verified_message_on_join(member)

        if member.avatar == None:
            avatar = 'https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702'
        else:
            avatar = member.avatar.url

        # Message to log channel
        if not (Config.get('greetings', 'enabled')):
            return
        logsChannel = self.bot.get_channel(Config.get('greetings', 'id'))
        if (member.bot):
            await self.bot.send_embed(logsChannel, description=f'Welcome {member.mention}, brother' , color='neutral')
        else:
            created = member.created_at
            created = created.strftime('%Y-%m-%d')
            description = f'**{joinedStatus}**\nMention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}\n\nInviter: <@{inviter.id}>\nInvite Code: {inviteCode}'
            footer_text=f'GS#Total: {member.guild.member_count} \u200b'
            await self.bot.send_embed(logsChannel, color='neutral', description=description, author_icon=avatar, author_name='User joined!', footer_text=footer_text, timestamp=True)

    #####################################
    ##           MEMBER LEFT           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'Player left: {member.mention}')
        leftStatus = ''
        verification = Database.get_user(member.id)
        if (verification['Status'] == 'JOINED'):
            leftStatus = 'NOT VERIFIED'
        elif(verification['Status'] == 'REJECTED'):
            leftStatus = 'REJECTED'
        elif(verification['Status'] == 'SPECTATOR'):
            leftStatus = 'SPECTATOR'
        elif(verification['Status'] == 'ACCESS'):
            nickname = Database.get_user(member.id)['Nickname']
            if (nickname != ''):
                self.bot.unregister_player(nickname)
            Database.set_status(member.id, 'CONFIRMED')
            leftStatus = 'HAD ACCESS'
        elif(verification['Status'] == 'CONFIRMED'):
            leftStatus = 'VERIFIED'

        # Message to log channel
        if not (Config.get('greetings', 'enabled')):
            return
        logsChannel = self.bot.get_channel(Config.get('greetings', 'id'))
        embed = discord.Embed(color = Config.getColor('error'))
        
        if member.avatar == None:
            avatar = 'https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702'
        else:
            avatar = member.avatar.url

        if (member.bot):
            await self.bot.send_embed(logsChannel, description=f'Goodbye {member.mention}, brother' , color='neutral')
        else:
            created = member.created_at
            created = created.strftime('%Y-%m-%d')
            description = f'**{leftStatus}**\nMention: {member.mention}\nName: {member.name}#{member.discriminator}\nCreated: {created}'
            footer_text=f'GS#Total: {member.guild.member_count} \u200b'
            await self.bot.send_embed(logsChannel, color='error', description=description, author_icon=avatar, author_name='User left!', footer_text=footer_text, timestamp=True)

    #############*********#############
    ##           FUNCTIONS           ##
    #############*********#############

    # Function for finding inviter
    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))