import datetime
from typing import List
import discord
import logging

from config import Config
from libs import Database
from discord.ext import commands

logger = logging.getLogger(__name__)

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info('Connecting Verification module')

    ###################################
    ##      Verification Status      ##
    ###################################
    @commands.command(name='status')
    @commands.has_role("Interviewer")
    async def status(self, ctx, id: int):
        status = Database.get_status(id)
        if (type(status) != None):
            embed = discord.Embed(color = Config.getColor('success'))
            embed.description = f'***Пользователь:*** {self.bot.get_user(id).mention}\n***Статус:*** {status[0][0]}\n***Описание:*** {status[0][1]}\n'
            await ctx.send(embed= embed)

    ###################################
    ##             Confirm           ##
    ###################################
    @commands.command(name='confirm')
    async def confirm(self, ctx, id: int = None):
        invitedList = Database.get_invited(ctx.author.id)
        if (id == None):
            if (invitedList == ()):
                stroke = 'Все приглашения обработаны.'
            else:
                stroke = '***Список приглашенных вами не подтвержденных пользователей:***\n'
                for invited in invitedList:
                    stroke += f'ID: `{invited[0]}` - {self.bot.get_user(int(invited[0])).mention}\n'
            await ctx.send(stroke)
            return
        if (invitedList == ()):
            await ctx.send(f'Пользователь либо не существует, либо уже подтвержден.')
            return
        for invited in invitedList:
            if invited[0] == id:
                if (Database.confirm(ctx.author.id, id)):
                    await ctx.send(f'Вы поручились за пользователя {self.bot.get_user(id).mention}!')
                    await self.new_confirmed_player(self.bot.get_user(id))
                    return
        await ctx.send(f'Пользователь либо не существует, либо уже подтвержден.')

    ###################################
    ##        Force-Confirm          ##
    ###################################
    @commands.command(name='force-confirm')
    @commands.has_role("Interviewer")
    async def force_confirm(self, ctx, id: int = None):
        invitedList = Database.get_all_invited()
        if (id == None):
            if (invitedList == ()):
                stroke = 'Все приглашения обработаны.'
            else:
                stroke = '***Список не подтвержденных пользователей:***\n'
                for invited in invitedList:
                    stroke += f'ID: `{invited[0]}` - {self.bot.get_user(int(invited[0])).mention}\n'
            await ctx.send(stroke)
            return
        if (invitedList == ()):
            await ctx.send(f'Пользователь либо не существует, либо уже подтвержден.')
            return
        for invited in invitedList:
            if invited[0] == id:
                if (Database.confirm(ctx.author.id, id)):
                    await ctx.send(f'Вы поручились за пользователя {self.bot.get_user(id).mention}!')
                    await self.new_confirmed_player(self.bot.get_user(id))
                    return
        await ctx.send(f'Пользователь либо не существует, либо уже подтвержден.')

    #############*********#############
    ##           FUNCTIONS           ##
    #############*********#############

    # channel: verification
    # Starting interview message
    async def new_confirmed_player(self, member: discord.Member):
        user = Database.get_user(member.id)
        Database.set_status(member.id, 'INTERVIE')
        confirmator = self.bot.get_user(user[0][9])
        description = f'{confirmator.mention} поручился за {member.mention}! Приступаем к формированию анкеты.\n'
        verificationChannel = self.bot.get_channel(Config.get('verification', 'channel'))
        await self.bot.send_embed(verificationChannel, description=description, color='success')

    # channel: verification
    # New unverified player 
    async def new_unconfirmed_player(self, member: discord.Member):
        description = f'Пользователь {member.mention} присоединился к серверу! Пока за него никто не поручился.\n'
        verificationChannel = self.bot.get_channel(Config.get('verification', 'channel'))
        #await verificationChannel.send(embed= embed)
        await self.bot.send_embed(verificationChannel, description=description, color='neutral')

    # channel: DM
    # Message to inviter that a new user joined
    async def send_inviter_message(self, member: discord.user, inviter: discord.user, invite: discord.invite):
        stroke = ''
        stroke += f'По вашему приглашению `{invite.code}` присоединился новый пользователь. Готовы ли вы за него поручиться? В таком случае игрок пройдет регистрацию в упрощенном формате.'
        stroke += f'\n\n*Пользователь* ID: `{member.id}` - {member.mention}'
        stroke += f'\n\nЧтобы поручиться за пользователя введите: `!confirm ID`'
        footer_text= f'Invite uses: {invite.uses} \u200b'
        await self.bot.send_embed(inviter, color='neutral', title='Приглашен игрок!', description=stroke, footer_text=footer_text, timestamp=True)

    # channel: DM
    # Message to newbie on first join
    async def send_newbie_message_on_join(self, member: discord):
        await self.bot.send_embed(member, color='neutral', description='Добро пожаловать на сервер GS#Private Vanilla MC! Вся информация в канале <#866711549233594398>')

    # channel: DM
    # Rejected message on join
    async def send_rejected_message_on_join(self, member: discord):
        description = 'У вас нет доступа к серверу. Это могло случиться, если вы не прошли верификацию или получили перманентый бан. Администратор последней надежды <@222746438814138368>.'
        await self.bot.send_embed(member, color='neutral', description=description)

    # channel: DM
    # Spectator message on join
    async def send_spectator_message_on_join(self, member: discord):
        description = 'Добро пожаловать на сервер GS#Private Vanilla MC! Роль Spectator была восстановлена.'
        await self.bot.send_embed(member, color='neutral', description=description)
    
    # channel: DM
    # Access message on join
    async def send_access_message_on_join(self, member: discord):
        description = 'Добро пожаловать на сервер GS#Private Vanilla MC! Доступ к майнкрафт серверу был аннулирован, чтобы его вернуть обратитесь к администратору.'
        await self.bot.send_embed(member, color='neutral', description=description)

    # channel: DM
    # Access message on join
    async def send_verified_message_on_join(self, member: discord):
        description = 'Добро пожаловать на сервер GS#Private Vanilla MC! Ваш статус верификации был восстановлен.'
        await self.bot.send_embed(member, color='neutral', description=description)

    # channel: players
    # New minecraft player message
    async def new_player_message(self, member: discord.Member):
        user = Database.get_user(member.id)
        stroke = f':small_orange_diamond: Никнейм: {user[0][4]}\n'
        stroke += f':small_orange_diamond: Реальное имя: {user[0][3]}\n'
        regDate = user[0][5].split(' ')
        stroke += f':small_orange_diamond: Дата регистрации: {regDate[0]}\n'
        stroke += f':small_blue_diamond: Дискорд: {member.mention}'
        playersChannel = self.bot.get_channel(Config.get('profile', 'channel'))
        await self.bot.send_embed(playersChannel, description=stroke, footer_text='GameSpace#Private \u200b', footer_icon='https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702', color='neutral', timestamp=True)

def setup(bot):
    bot.add_cog(VerificationCog(bot))