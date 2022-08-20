import discord

from ..user import GalacticUser, Player

from ..paginator.page import Page

from .account_page import AccountPage

from ..elements.custom_button import CustomButton
from ..elements.dropdown import Dropdown

from config import get_color
from logger import log_debug

class AccountSelectionPage(Page):
    def __init__(self, menu_message):
        self.menu_message = menu_message
        super().__init__()

    @classmethod
    async def create(cls, menu_message):
        self = AccountSelectionPage(menu_message)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Create dropdown
        options = []
        galactic_user: GalacticUser = self.menu_message.galactic_user
        for player in galactic_user.players:
            options.append({'label': player.realname, 'description': player.groups[0].value['name'], 'emoji': player.groups[0].value['emoji']})
        dropdown = Dropdown(self.menu_message, 'Мои аккаунты', options)
        dropdown.set_callback(self.dropdown_callback)
        # Add to view items
        self.view_items.append(dropdown)
        self.view_items.append(self.menu_message.get_return_button())
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        # Title
        embed.color = get_color('neutral')
        embed.description = 'Пожалуйста, выберите аккаунт с которым вы хотите работать:'
        self.embed = embed

    async def dropdown_callback(self, realname: str):
        log_debug(f'Dropdown ckicked {realname}')
        username = realname.lower()
        for player in self.menu_message.galactic_user.players:
            if (player.username == username):
                await self.menu_message.switch_page(await AccountPage.create(self.menu_message, player))
                return