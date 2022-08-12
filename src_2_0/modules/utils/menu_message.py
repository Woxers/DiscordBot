import discord

from config import get_color
from logger import log_error, log_info, log_debug, log_warning

from discord.ui import View

from .menu.main_page import MainPage

from .database.players_db import PlayersDatabase
from .database.luckyperms_db import LuckyPermsDatabase

class MenuView(View):
    def __init__(self, menu_message , timeout = 120):
        self.menu_message = menu_message
        super().__init__(timeout=timeout)

    async def on_timeout(self):
        await self.menu_message.close('timeout')

class MenuMessage():
    def __init__(self, bot, user, channel):
        self.bot = bot                              # Galactic Bot

        self.user = bot.get_member_by_id(user.id)   # Interaction user
        self.info = None                            # User information

        self.channel = channel                      # Channel where to send message
        self.message = None                         # Discord message

        self.view = MenuView(self, timeout=120)     # Main View

        self.page_stack = []                        # Page stack

    # Prepare information and switch page to 'main'
    async def setup_menu_message(self):
        await self.prepare_information()
        await self.switch_page('main_page')
        self.message = await self.channel.send(embed=self.page_stack[-1].get_embed(), view=self.view)

    # Prepare menu information
    async def prepare_information(self):
        try:
            self.info = PlayersDatabase.get_user_by_id(self.user.id)
            players = PlayersDatabase.get_players_by_id(self.user.id)
            for nickname in players:
                players[nickname]['permissions'] = LuckyPermsDatabase.get_player_permissions(nickname)
                players[nickname]['settings'] = PlayersDatabase.get_player_settings(nickname)
            self.info['players'] = players
        except Exception as e:
            log_error(e)
            raise(e)

    # Update message
    async def update(self):
        await self.message.edit(embed=self.page_stack[-1].get_embed(), view=self.view)

    # Switch to previous page
    async def previous_page(self):
        if (len(self.page_stack) > 1):
            self.page_stack.pop()
            await self.channel.send(embed=self.page_stack[-1].get_embed(), view=self.view)
            return 1
        else:
            return 0

    # Close message
    async def close(self, reason: str = None):
        # Clear items
        self.view.clear_items()
        del self.page_stack[:]
        # Edit message to closed
        embed = discord.Embed()
        embed.color = get_color('neutral')
        reason = '' if reason == None else ': `' + reason + '`'
        embed.description = f'Работа меню завершена{reason}'
        await self.message.edit(embed = embed, view = None)
        # Remove message from list
        del self.bot.get_cog('MenuCog').menu_messages[str(self.user.id)]
        log_debug(f'Menu was closed with reason: {reason}')

    # Select page
    async def switch_page(self, type: str):
        try:
            if (type == 'main_page'):
                self.view.clear_items()
                main_page = await MainPage.create(self)
                for item in main_page.get_view_items():
                    self.view.add_item(item)
                self.page_stack.append(main_page)
                log_debug('Switch page to MainPage')
            elif (type == 'accounts_page'):
                log_debug('Switch page to AccountsPage')
            else:
                raise ValueError(f'There is no page with name {type}')
        except Exception as e:
            log_error(e)
            raise(e)
