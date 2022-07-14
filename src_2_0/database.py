import time
import pymysql

import hashlib
import secrets

from config import get_color, config
from logger import log_info, log_error

# Singleton
class Database:
    __instance = None
    __connection = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
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
            connection = pymysql.connect(host=config['database']['host'], user=config['database']['user'], passwd=config['database']['passwd'], db=config['database']['db_name'])
            connection.set_charset('utf8')
            log_info('Connection to MySQL database')
        except pymysql.Error as e:
            log_error(f'Cannot connect to Database!\n' + str(e))
            raise SystemExit('[SystemExit] Cannot connect to Database!')
        return connection

    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        if (cls.__connection.open == False):
            cls.reload_connection()
        cursor = cls.__connection.cursor()
        try:
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except pymysql.Error as err_string:
            log_error(f'The exception in execute_query occured, {err_string}')
            return -1

    @classmethod
    def authme_check_nickname(cls, nickname: str):
        '''
        Check if nickname already in use

        Return values: 

            Exist: 1

            Not Exist: 0
        '''
        result = cls.execute_query(f'SELECT CheckNickname("{nickname}")')
        if (result == -1):
            return 1
        else:
            return result[0][0]

    @classmethod
    def authme_register_player(cls, user_id: int, nickname: str, password: str):
        '''
        Register player on minecraft server

        Return values: 

            Registered: 1

            Failed: 0
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
        result = cls.execute_query(f'CALL RegisterPlayer({user_id}, "{nickname}", "{password}", "{timestamp}")')
        if (result == -1):
            return 0
        else:
            return 1
    
    @classmethod
    def ckeck_user(cls, user_id: int):
        '''
        Check if discord user already in database

        Return values: 

            Exist: 1

            Not Exist: 0
        '''
        result = cls.execute_query(f'SELECT CheckUser({user_id})')
        if (result == -1):
            return 1
        else:
            return result[0][0]

    @classmethod
    def get_user_by_id(cls, user_id: int):
        '''
        Get discord user info by id 

        Return values: 

            Success:

                dict: {'id', 'inviter_id', 'status'}

            User not exist:

                None
        '''
        result = cls.execute_query(f'SELECT * FROM discord WHERE id = {user_id}')
        if (result == -1):
            return None
        else:
            user = dict()
            user['id'] = result[0][0]
            user['inviter_id'] = result[0][1]
            user['status'] = result[0][2]
            return user

    @classmethod
    def get_user_by_nickname(cls, nickname: str):
        '''
        Get discord user info by nickname

        Return values: 

            Success:

                dict: {'id', 'inviter_id', 'status'}

            User not exist:

                None
        '''
        result = cls.execute_query(f'CALL GetUserByNickname("{nickname}")')
        if (result == -1):
            return None
        else:
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

            Success:

                dict: {'username': {'realname', 'ip', 'lastlogin', 'regdate', 'isLogged'}}

            User not exist:

                None
        '''
        result = cls.execute_query(f'CALL GetPlayersByUserID({user_id})')
        if (result == -1):
            return None
        else:
            players = dict()
            for player_info in result:
                players[player_info[0]] = {'realname': player_info[1], 'ip': player_info[2], 'lastlogin': player_info[3], 'regdate': player_info[4], 'isLogged': player_info[5]}
            return players

    def set_status_by_user_id(cls, user_id: int, status: str):
        '''
        Set player's status

        Return values: 

            Success: 1

            Failed: 0
        '''
        result = cls.execute_query(f'UPDATE discord SET status = "{status}" WHERE id = {user_id} LIMIT 1')
        if (result == -1):
            return 0
        else:
            return 1

db = Database()