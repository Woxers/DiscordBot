import discord

from ..user import GalacticUser, Player
from ..paginator.page import Page
from ..elements.custom_button import CustomButton

from .account_selector_page import AccountSelectionPage

from config import get_color
from logger import log_debug


class MainPage(Page):
    def __init__(self, menu_message):
        self.menu_message = menu_message
        super().__init__()

    @classmethod
    async def create(cls, menu_message):
        self = MainPage(menu_message)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Creating accounts button
        accounts_button = CustomButton(discord.ButtonStyle.green, 'Аккаунты')
        accounts_button.set_callback(self.accounts_button_callback)
        # Append item list
        self.view_items.append(self.menu_message.get_return_button())
        self.view_items.append(accounts_button)
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        galactic_user: GalacticUser = self.menu_message.galactic_user
        # Title
        embed.title = 'Меню пользователя'
        # Description
        status = f"{galactic_user.status.value['name']} {galactic_user.status.value['emoji']}" 
        status_description = galactic_user.status.value['description']
        inviter_id = galactic_user.inviter_id
        joined = galactic_user.user.joined_at.strftime('%Y-%m-%d %H:%M')
        embed.description = f'Статус верификации: `{status}`\nОписание: `{status_description}`\n\nПригласивший: <@{inviter_id}>\nПрисоединился: `{joined}`'
        # Color
        embed.color = get_color('neutral')
        # Picture
        if (self.menu_message.user.avatar == None):
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702')
        else:
            embed.set_thumbnail(url=self.menu_message.user.avatar.url)
        # Fields
        players: list[Player] = galactic_user.players
        for player in players:
            active = 'да' if galactic_user.status.name == 'access' and player.has_access == 1 else 'нет'
            role_name = f"{player.groups[0].value['name']} {player.groups[0].value['emoji']}"
            date = player.reg_date.strftime('%Y-%m-%d')
            embed.add_field(name=player.realname, inline=1, value=f'Активен: `{active}`\nРоль: `{role_name}`\nНаиграно: `IN_DEV`\nЗарегистрирован: `{date}`')
        self.embed = embed
    
    async def accounts_button_callback(self):
        await self.menu_message.switch_page(await AccountSelectionPage.create(self.menu_message))
        log_debug('accounts button callback')