import asyncio
import logging
import discord

from config import Config
from discord.ext import commands

from libs import Database

logger = logging.getLogger(__name__)

class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()
        logger.info('Connecting Messages module')


        # CHANNEL: Verification
    # Starting interview message
    async def new_confirmed_player(self, member: discord.Member, confirmator: discord.Member):
        description = f'Пользователь {member.mention} присоединился к серверу, пригласивший {confirmator.mention} за него поручился!\n'
        verificationChannel = self.bot.get_channel(Config.get('verification', 'channel'))
        await self.bot.send_embed(verificationChannel, description=description, color='success')

        # CHANNEL: Verification
    # New unverified player 
    async def new_unconfirmed_player(self, member: discord.Member, confirmator: discord.Member):
        description = f'Пользователь {member.mention} присоединился к серверу, пригласивший {confirmator.mention} за него не поручился.\n'
        verificationChannel = self.bot.get_channel(Config.get('verification', 'channel'))
        await self.bot.send_embed(verificationChannel, description=description, color='error')

        # CHANNEL: DM Inviter
    # Message to inviter that a new user joined
    async def send_inviter_message(self, member: discord.user, inviter: discord.user, invite: discord.invite):
        stroke = ''
        stroke += f'По вашему приглашению `{invite.code}` присоединился новый пользователь. Готовы ли вы за него поручиться? В таком случае пользователь пройдет верификацию в упрощенном формате.'
        stroke += f'\n\n*User* ID: `{member.id}` - {member.mention}'
        footer_text= f'Invite uses: {invite.uses} \u200b'
        view = self.View()
        view.bot = self.bot
        view.member = member
        view.confirmator = inviter
        msg = await self.bot.send_embed(inviter, color='neutral', title='Приглашен игрок!', description=stroke, footer_text=footer_text, timestamp=True, view=view)
    class View(discord.ui.View):
        bot = None
        member = None
        confirmator = None
        # Кнопка Поручиться
        @discord.ui.button(label="Поручиться!", style=discord.ButtonStyle.green)
        async def confirm_callback(self, interaction, button):
            embed = discord.Embed(color = Config.getColor('success'))
            embed.description = f'Вы поручились за пользователя {self.member.mention}!'
            await interaction.response.edit_message(view = None, embed = embed)
            await self.bot.get_cog('MessagesCog').new_confirmed_player(self.member, self.confirmator)
        # Кнопка Я не знаю кто это
        @discord.ui.button(label="Я не знаю кто это", style=discord.ButtonStyle.red)
        async def un_confirm_callback(self, interaction, button):
            embed = discord.Embed(color = Config.getColor('error'))
            embed.description = f'Вы не стали поручаться за пользователя {self.member.mention}!'
            await interaction.response.edit_message(view = None, embed = embed)
            await self.bot.get_cog('MessagesCog').new_unconfirmed_player(self.member, self.confirmator)

        

        # CHANNEL: DM Newbie
    # Message to newbie on first join
    async def send_newbie_message_on_join(self, member: discord.Member):
        await self.bot.send_embed(member, color='neutral', description='Добро пожаловать на сервер GS#Private Vanilla MC! Если ты хочешь играть вместе с нами, ознакомься с информацией для новичков в канале <#866711549233594398>')

        # CHANNEL: DM
    # Rejected message on join
    async def send_rejected_message_on_join(self, member: discord.Member):
        description = 'Ваша кандидатура была отклонена. Администратор последней надежды <@222746438814138368>.'
        await self.bot.send_embed(member, color='neutral', description=description)

        # CHANNEL: DM
    # Spectator message on join
    async def send_spectator_message_on_join(self, member: discord.Member):
        description = 'Рады снова Вас видеть! Роль Spectator была восстановлена.'
        await self.bot.send_embed(member, color='neutral', description=description)
    
    # channel: DM
    # Access message on join
    async def send_access_message_on_join(self, member: discord.Member):
        description = 'Рады снова Вас видеть! Ваш статус верификации был восстановлен.'
        await self.bot.send_embed(member, color='neutral', description=description)
        description = 'Доступ к майнкрафт серверу был аннулирован, чтобы его вернуть обратитесь к администрации (<@&867811212426870804>).'
        await self.bot.send_embed(member, color='error', description=description)

    # channel: DM
    # Access message on join
    async def send_verified_message_on_join(self, member: discord.Member):
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

async def setup(bot):
    await bot.add_cog(MessagesCog(bot))