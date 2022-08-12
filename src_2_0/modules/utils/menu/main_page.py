from datetime import datetime
import discord

from config import get_color

from .elements.accounts_button import AccountsButton
from .elements.close_button import CloseButton
from .elements.return_button import ReturnButton

class MainPage():
    def __init__(self, menu_message):
        self.menu_message = menu_message        # MenuMessage
        self.embed = None                       # Embeded part
        self.view_items = []                    # Buttons, Selection and other

    @classmethod
    async def create(cls, menu_message):
        self = MainPage(menu_message)
        await self.create_embed()
        await self.create_view()
        return self

    async def create_view(self):
        self.view_items.append(ReturnButton(self.menu_message))
        self.view_items.append(AccountsButton(self.menu_message))
        self.view_items.append(CloseButton(self.menu_message))

    async def create_embed(self):
        embed = discord.Embed()
        # Title
        embed.title = 'Меню пользователя'
        # Description
        status = self.menu_message.info['status'].upper()
        access = 'есть' if self.menu_message.info["status"] == 'access' else 'нет'
        inviter_id = self.menu_message.info['inviter_id']
        joined = self.menu_message.user.joined_at.strftime('%Y-%m-%d %H:%M')
        embed.description = f'Статус верификации: `{status}`\nДоступ к серверу: `{access}`\n\nПригласивший: <@{inviter_id}>\nПрисоединился: `{joined}`'
        # Color
        embed.color = get_color('neutral')
        # Picture
        if (self.menu_message.user.avatar == None):
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702')
        else:
            embed.set_thumbnail(url=self.menu_message.user.avatar.url)
        # Fields
        players = self.menu_message.info['players']
        for nickname in players:
            active = 'да' if self.menu_message.info["status"] == 'access' and players[nickname]['has_access'] == 1 else 'нет'
            role_name = 'Игрок'
            for permission in players[nickname]['permissions']:
                if (permission['name'] == 'group.admin'):
                    role_name = 'Администратор'
                if (permission['name'] == 'group.stuff'):
                    role_name = 'Модератор'
            date = datetime.utcfromtimestamp(int(players[nickname]['regdate']) / 1000).strftime('%Y-%m-%d')
            embed.add_field(name=players[nickname]['realname'], inline=1, value=f'Активен: `{active}`\nРоль: `{role_name}`\nНаиграно: `IN_DEV`\nЗарегистрирован: `{date}`')
        self.embed = embed

    # Get discord.Embed
    def get_embed(self):
        return self.embed
    
    # Get discord.ui.View
    def get_view_items(self):
        return self.view_items