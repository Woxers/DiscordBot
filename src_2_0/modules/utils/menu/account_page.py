import discord

from ..user import GalacticUser, Player
from ..paginator.page import Page
from ..elements.custom_button import CustomButton

from ..mc_skins import SkinProvider

from config import get_color
from logger import log_debug

class AccountPage(Page):
    def __init__(self, menu_message, player: Player):
        self.player: Player = player
        self.menu_message = menu_message
        super().__init__()

    @classmethod
    async def create(cls, menu_message, player):
        self = AccountPage(menu_message, player)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Creating accounts button
        settings_button = CustomButton(discord.ButtonStyle.green, 'Настройки')
        settings_button.set_callback(self.settings_button_callback)
        # Append item list
        self.view_items.append(self.menu_message.get_return_button())
        self.view_items.append(settings_button)
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        galactic_user = self.menu_message.galactic_user
        if (self.player.head == None):
            self.player.head = SkinProvider.get_head(self.player.realname)
        self.attachment = discord.File(self.player.head, filename='image.png')
        embed.set_thumbnail(url="attachment://image.png")
        # Title
        active = '(Активен)' if galactic_user.status.name == 'access' and self.player.has_access == 1 else '(Неактивен)'
        embed.title = f"{self.player.realname} {active}"
        # Color
        embed.color = get_color('neutral')
        # Base information field
        role_name = f"{self.player.groups[0].value['name']} {self.player.groups[0].value['emoji']}"
        reg_date = self.player.reg_date.strftime('%Y-%m-%d')
        embed.add_field(name='Основная информация', value=f"Основная роль: `{role_name}`\nНаиграно: `IN_DEV`\nЗарегистрирован: `{reg_date}`", inline=1)
        # # Last Session field
        # last_ip = self.player.last_ip
        # last_login = self.player.last_login.strftime('%Y-%m-%d')
        # embed.add_field(name='Последний вход', value=f"IP-Адрес: `{last_ip}`\nДата: `{last_login}`", inline=1)
        # Groups field
        {'name': 'Администратор', 'emoji': '🟥', 'weight': 100, 'primary': 1}
        group_text = ''
        for group in self.player.groups:
            group_text += f"`{group.value['name']} {group.value['emoji']}`\n"
        embed.add_field(name='Группы', value=group_text, inline=1)
        self.embed = embed
    
    async def settings_button_callback(self):
        log_debug('settings button callback')