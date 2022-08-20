from asyncio import sleep
import time
import pymysql

import hashlib
import secrets

from config import config
from logger import log_debug, log_info, log_error, log_critical, log_warning

# Singleton
class PlayersDatabase:
    __instance = None
    __connection = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(PlayersDatabase, cls).__new__(cls)
            cls.__connection = cls.create_connection()
            return cls.__instance

    # Refresh connection
    @classmethod
    def reload_connection(cls):
        cls.__connection = cls.create_connection()

    # Connecting database
    @classmethod
    def create_connection(cls):
        try:
            connection = None
            connection = pymysql.connect(host=config['players_database']['host'], user=config['players_database']['user'], passwd=config['players_database']['passwd'], db=config['players_database']['db_name'])
            connection.set_charset('utf8')
            log_info('Connection to MySQL database')
        except pymysql.Error as e:
            log_critical(f'Cannot connect to Database!\n' + str(e))
            raise SystemExit('Cannot connect to Database!')
        return connection

    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        if (not cls.test_query()):
            sleep(2)
            cls.reload_connection()
        try:
            cursor = cls.__connection.cursor()
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except pymysql.Error as e:
            log_error(f'Exception in execute_query occured, {e}')
            raise(e)

    # Test query
    @classmethod
    def test_query(cls):
        try:
            cursor = cls.__connection.cursor()
            cursor.execute('select * from discord limit 1')
            cls.__connection.commit()
            return 1
        except Exception as e:
            log_debug(f'Exception in test_query occured {e}')
            return 0

    @classmethod
    def authme_check_nickname(cls, nickname: str):
        '''
        Check if nickname already in use

        Return values:
        -------------
            `1` - exist

            `0` - not Exist
        '''
        result = cls.execute_query(f'SELECT CheckNickname("{nickname}")')
        if (not result):
            raise(Exception('Exception in authme_check_nickname, there is no query result'))
        return result[0][0]

    @classmethod
    def register_player(cls, user_id: int, nickname: str, password: str):
        '''
        Register player on minecraft server
        '''
        if (cls.authme_check_nickname(nickname)):
            return 0
        # authme SHA256 encryption
        salt = secrets.token_hex(8)
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        hash += salt
        hash = hashlib.sha256(hash.encode('utf-8')).hexdigest()
        password = f'$SHA${salt}${hash}'
        # adding to database
        timestamp = int(time.time() * 1000)
        cls.execute_query(f'CALL RegisterPlayer({user_id}, "{nickname}", "{password}", "{timestamp}")')
        return 1

    @classmethod
    def add_user(cls, user_id: int, inviter_id: int, status: str = None):
        '''
        Add new user to database
        '''
        if (status == None):
            status = 'joined'
        cls.execute_query(f'CALL AddUser({user_id}, {inviter_id}, "{status}")')
        return 1
    
    @classmethod
    def ckeck_user(cls, user_id: int):
        '''
        Check if discord user already in database

        Return values: 
        -------------
            `1` - exist

            `0` - not Exist
        '''
        result = cls.execute_query(f'SELECT CheckUser({user_id})')
        if (not result):
            raise(Exception('Exception in ckeck_user, there is no query result'))
        return result[0][0]

    @classmethod
    def get_user_by_id(cls, user_id: int):
        '''
        Get discord user info by id 

        Return values: 
        -------------
                dict: `{'id', 'inviter_id', 'status'}`
        '''
        result = cls.execute_query(f'SELECT * FROM discord WHERE id = {user_id}')
        if (not result):
            raise(Exception('Exception in get_user_by_id, there is no query result'))
        user = dict()
        user['id'] = result[0][0]
        user['inviter_id'] = result[0][1]
        user['status'] = result[0][2]
        return user
    
    @classmethod
    def get_raw_player_by_id(cls, authme_id: int):
        '''
            Get player by id\n
            Return values: 
            -------------
                array: `['id', 'username', 'realname', 'ip', 'lastlogin', 'regdate', 'isLogged', 'has_access']`
        '''
        result = cls.execute_query(f'SELECT id, username, realname, ip, lastlogin, regdate, isLogged, has_access from authme where id = {authme_id}')
        if (not result):
            raise(Exception('Exception in get_user_by_id, there is no query result'))
        return result[0]

    @classmethod
    def get_invited_count_by_id(cls, user_id: int):
        '''
        Get invited count by user id

        Return values: 
        -------------
                'int'
        '''
        result = cls.execute_query(f'SELECT GetInvitedByUserCount({user_id})')
        if (not result):
            raise(Exception('Exception in get_invited_count_by_id, there is no query result'))
        return result[0][0]

    @classmethod
    def get_invited_players_count_by_id(cls, user_id: int):
        '''
        Get invited PLAYERS count by user id

        Return values: 
        -------------
                'int'
        '''
        result = cls.execute_query(f'SELECT GetInvitedPlayersCountByUser({user_id})')
        if (not result):
            raise(Exception('Exception in get_invited_players_count_by_id, there is no query result'))
        return result[0][0]

    @classmethod
    def get_user_by_nickname(cls, nickname: str):
        '''
        Get discord user info by nickname

        Return values: 
        -------------
                dict: `{'id', 'inviter_id', 'status'}`
        '''
        result = cls.execute_query(f'CALL GetUserByNickname("{nickname}")')
        if (not result):
            raise(Exception('Exception in get_user_by_nickname, there is no query result'))
        user = dict()
        user['id'] = result[0][0]
        user['inviter_id'] = result[0][1]
        user['status'] = result[0][2]
        return user

    @classmethod
    def get_players_by_id(cls, user_id: int):
        '''
        Get players by discord user id (get mc accounts of user)

        Return values: 
        -------------
                dict: `{'username': {'id', 'realname', 'ip', 'lastlogin', 'regdate', 'isLogged', 'has_access'}}`
        '''
        result = cls.execute_query(f'CALL GetPlayersByUserID({user_id})')
        if (not result):
            raise(Exception('Exception in get_players_by_id, there is no query result'))
        players = dict()
        for player_info in result:
            players[player_info[0]] = {'id': player_info[7], 'realname': player_info[1], 'ip': player_info[2], 'lastlogin': player_info[3], 'regdate': player_info[4], 'isLogged': player_info[5], 'has_access': player_info[6]}
        return players

    @classmethod
    def set_status_by_user_id(cls, user_id: int, status: str):
        '''
        Set player's status
        '''
        cls.execute_query(f'UPDATE discord SET status = "{status}" WHERE id = {user_id}')
        return 1

    @classmethod
    def set_new_player_password(cls, nickname: str, password: str):
        '''
        Update player password
        '''
        if (not cls.authme_check_nickname(nickname)):
            return 0
        # authme SHA256 encryption
        salt = secrets.token_hex(8)
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        hash += salt
        hash = hashlib.sha256(hash.encode('utf-8')).hexdigest()
        password = f'$SHA${salt}${hash}'
        # Update value in database
        cls.execute_query(f'UPDATE authme SET password = "{password}" WHERE username = "{nickname}" LIMIT 1')
        return 1

    @classmethod
    def get_player_settings(cls, nickname: str):
        '''
        Get player settings

        Return values: 
        -------------
                dict: `{'authme_id', 'quick_auth', 'join_notify'}`
        '''
        result = cls.execute_query(f'select * from player_settings where authme_id = (select id from authme where username = "{nickname}")')
        if (not result):
            raise(Exception('Exception in get_player_settings, there is no query result'))
        if (result == -1):
            return None
        dt = {}
        dt['authme_id'] = result[0][0]
        dt['quick_auth'] = result[0][1]
        dt['join_notify'] = result[0][2]
        return dt

db = PlayersDatabase()