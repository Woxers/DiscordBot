import discord

from datetime import datetime

from logger import log_warning

from .enums.mc_settings import McSettings
from .enums.mc_groups import McGroups
from .enums.statuses import Statuses

from .database.players_db import PlayersDatabase
from .database.luckyperms_db import LuckyPermsDatabase

def convert_unix_ts(timestamp) -> datetime:
    return datetime.utcfromtimestamp(int(timestamp) / 1000) #.strftime('%Y-%m-%d %H:%M')

class Player():
    '''
        `id: int` Authme ID\n
        `username: str` Player's realname.lower()\n
        `realname: str` Player's nickname\n
        `last_ip: str` Last login IP Address\n
        `last_login: datetime` Last login Datetime\n
        `reg_date: datetime` Registration Datetime\n
        `is_logged: bool` Is player logged in\n
        `has_access: bool` Player has access\n
        `groups: list[McGroups]` McGroups ordered list\n
        
        `settings: dict` 
            {
                'quick_auth_enabled', \n
                'join_notify_enabled'
            }
    '''
    def __init__(self, id):
        self.id: int = id                   # Authme ID

        self.username: str = None           # Player's realname.lower()
        self.realname: str = None           # Player's nickname
        self.last_ip: str = None            # Last login IP Address
        self.last_login: datetime = None    # Last login Datetime
        self.reg_date: datetime = None      # Registration Datetime 
        self.is_logged: bool = None         # Is player logged in
        self.has_access: bool = None        # Player has access

        self.groups: list[McGroups] = []    # McGroups list

        self.settings = []                  # Player's settings

        self.head = None                    # Players head

        self.weight: int = 1                # For sorting

        try:
            self.init_authme()
            self.init_groups()
            self.init_settings()
        except Exception as e:
            print(e)
            raise(e)

    def init_authme(self):
        raw_player = PlayersDatabase.get_raw_player_by_id(self.id)
        self.username = raw_player[1]
        self.realname = raw_player[2]
        self.last_ip = raw_player[3]

        self.last_login = convert_unix_ts(raw_player[4])
        self.reg_date = convert_unix_ts(raw_player[5])

        self.is_logged = raw_player[6]
        self.has_access = raw_player[7]

    def init_groups(self):
        ''''
            Get group list
        '''
        raw_permissions = LuckyPermsDatabase.get_player_permissions(self.username)
        for permission in raw_permissions:
            if (permission['name'].startswith('group.')):
                group_name = permission['name'].partition('.')[2]
                group = McGroups.get(group_name)
                if (group != None):
                    self.groups.append(group)
                else:
                    log_warning(f'There is no group with name: {group_name}')
        self.groups.sort(key=McGroups.get_comparator(), reverse=1)
        if (len(self.groups) > 0):
            self.weight = self.groups[0].value['weight']

    def init_settings(self):
        '''
            Get player settings
        '''
        self.settings = PlayersDatabase.get_player_settings(self.username)

    def set_settings_value(self, key, value):
        PlayersDatabase.set_settings_value(self.id, key, value)

    @classmethod
    def compare(cls, item1, item2):
        print(f'{item1.name} vs {item2.name}')
        if (item1.weight > item2.weight):
            return 1
        return -1
        
class GalacticUser():
    '''
        `user: discord.member` Discord account\n
        `inviter_id: int` Inviter id\n
        `status: Statuses` Status\n
        `invited_players: int` Invited players count\n
        `invited: int` Invited users count\n
        `players: list[Player]` Players (MC Server Accounts)\n
    '''
    def __init__(self, member: discord.member):
        self.user = member                      # Discord account
        self.inviter_id: int = None             # Inviter id

        self.status: Statuses = None            # Status

        self.invited_players: int = 0           # Invited players count
        self.invited: int = 0                   # Invited users count

        self.players: list[Player] = []         # Players (MC Server Accounts)
        
        self.init()

    def init(self):
        # Get invited
        self.invited = PlayersDatabase.get_invited_count_by_id(self.user.id)
        self.invited_players = PlayersDatabase.get_invited_players_count_by_id(self.user.id)

        # Get user
        raw_user = PlayersDatabase.get_user_by_id(self.user.id)
        self.inviter_id = raw_user['inviter_id']
        self.status = Statuses.get(raw_user['status'])
        # Get players
        user_accounts = PlayersDatabase.execute_query(f'select player_id from authme_discord where discord_id = {self.user.id}')
        for id in user_accounts:
            self.players.append(Player(id[0]))