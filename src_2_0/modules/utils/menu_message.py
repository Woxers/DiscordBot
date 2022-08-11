from logger import log_error, log_info, log_debug, log_warning

from .menu.main_page import MainPage

from .database.players_db import PlayersDatabase
from .database.luckyperms_db import LuckyPermsDatabase

class MenuMessage():
    def __init__(self, bot, user, channel):
        self.bot = bot                              # Galactic Bot

        self.user = bot.get_member_by_id(user.id)   # Interaction user
        self.info = None                            # User information

        self.channel = channel                      # Channel where to send message
        self.message = None                         # Discord message

        self.page_stack = []                        # Page stack

    async def setup_menu_message(self):
        await self.prepare_information()
        await self.switch_page('main_page')
        await self.channel.send(embed=self.page_stack[-1].get_embed())

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

    # Select page
    async def switch_page(self, type: str):
        try:
            if (type == 'main_page'):
                main_page = await MainPage.create(self)
                self.page_stack.append(main_page)
                log_debug('Switch page to MainPage')
        except Exception as e:
            log_error(e)
            raise(e)
