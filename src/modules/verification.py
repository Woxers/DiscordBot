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
        print(status)
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

    # Отправляет сообщение о новом игроке
    async def new_player_message(self, member: discord.Member):
        user = Database.get_user(member.id)
        stroke = f':small_orange_diamond: Никнейм: {user[0][4]}\n'
        stroke += f':small_orange_diamond: Реально имя: {user[0][3]}\n'
        regDate = user[0][5].split(' ')
        stroke += f':small_orange_diamond: Дата регистрации: {regDate[0]}\n'
        stroke += f':small_blue_diamond: Дискорд: {member.mention}'
        playersChannel = self.bot.get_channel(Config.get('profile', 'channel'))
        embed = discord.Embed(color = Config.getColor('neutral'))
        embed.description = stroke
        embed.set_footer(text='GameSpace#Private \u200b', icon_url="https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702")
        embed.timestamp = timestamp=datetime.datetime.utcnow()
        await playersChannel.send(embed= embed)

    # Отправляет сообщение о неподтвержденном игроке
    async def new_unconfirmed_player(self, member: discord.Member):
        embed = discord.Embed(color = Config.getColor('neutral'))
        embed.description = f'Пользователь {member.mention} присоединился к серверу! Пока за него никто не поручился.\n'
        verificationChannel = self.bot.get_channel(Config.get('verification', 'channel'))
        await verificationChannel.send(embed= embed)

    # Обработка события появления нового подтвержденного пользователя
    async def new_confirmed_player(self, member: discord.Member):
        user = Database.get_user(member.id)
        Database.set_status(member.id, 'INTERVIE')
        confirmator = self.bot.get_user(user[0][9])
        embed = discord.Embed(color = Config.getColor('success'))
        embed.description = f'{confirmator.mention} поручился за {member.mention}! Приступаем к формированию анкеты.\n'
        verificationChannel = self.bot.get_channel(Config.get('verification', 'channel'))
        await verificationChannel.send(embed= embed)

def setup(bot):
    bot.add_cog(VerificationCog(bot))