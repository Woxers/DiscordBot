import time
import secrets
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

    # Check if nickname already exists
    # Return 'True' - if exists, else - 'False'
    @classmethod
    def authme_check_nickname(cls, nickname: str):
        result = cls.execute_query(f'SELECT CheckNickname("{nickname}")')
        if (result == -1):
            return 1
        else:
            return result[0][0]

    # Register player on minecraft server
    # Return 'True' if successfully registered, else - 'False'
    @classmethod
    def authme_register_player(cls, user_id: int, nickname: str, password: str):
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
    
    # Check if user already exists in database
    # Return 'True' - if exists, else - 'False'
    @classmethod
    def discord_ckeck_user(cls, user_id: int):
        result = cls.execute_query(f'SELECT CheckUser({user_id})')
        if (result == -1):
            return 1
        else:
            return result[0][0]

    # Gets user by id from database
    # Returns dict: id, inviter_id, status
    @classmethod
    def discord_get_user_by_id(cls, user_id: int):
        result = cls.execute_query(f'SELECT * FROM discord WHERE id = {user_id}')
        if (result == -1):
            return 0
        else:
            user = dict()
            user['id'] = result[0][0]
            user['inviter_id'] = result[0][1]
            user['status'] = result[0][2]
            return user

    # Gets user_id by nickname from database
    # Returns user_id if success, else - int(0)
    @classmethod
    def get_user_id_by_nickname(cls, nickname: str):
        result = cls.execute_query(f'SELECT GetUserIdByNickname("{nickname}")')
        if (result == -1):
            return 0
        else:
            if (result[0][0] == None):
                return 0
            return result[0][0]

# def authmeSHA256(password: str, salt: str = None):
#     if (salt == None):
#         salt = secrets.token_hex(8)
#     hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
#     hash += salt
#     hash = hashlib.sha256(hash.encode('utf-8')).hexdigest()
#     return f'$SHA${salt}${hash}'

db = Database()