from asyncio import sleep
import pymysql

from config import config
from logger import log_debug, log_info, log_error, log_critical

# Singleton
class LuckyPermsDatabase:
    __instance = None
    __connection = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(LuckyPermsDatabase, cls).__new__(cls)
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
            connection = pymysql.connect(host=config['luckyperms_database']['host'], user=config['luckyperms_database']['user'], passwd=config['luckyperms_database']['passwd'], db=config['luckyperms_database']['db_name'])
            connection.set_charset('utf8')
            log_info('Connection to MySQL database')
        except pymysql.Error as e:
            log_critical(f'Cannot connect to Database!\n' + str(e))
            raise SystemExit('Cannot connect to Database!')
        return connection

    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        while (not cls.test_query()):
            cls.reload_connection()
            sleep(3)
        cursor = cls.__connection.cursor()
        try:
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except pymysql.Error as e:
            log_error(f'Exception in execute_query occured, {e}')
            raise(e)
            return -1

    @classmethod
    def test_query(cls):
        try:
            cursor = cls.__connection.cursor()
            cursor.execute('select * from luckperms_actions limit 1')
            cls.__connection.commit()
            return 1
        except Exception as e:
            log_debug(f'Exception in test_query occured {e}')
            return 0

    @classmethod
    def get_player_uuid(cls, nickname: str):
        result = cls.execute_query(f'SELECT uuid from luckperms_players where username = LOWER("{nickname}")')
        if (not result):
            raise(Exception('Exception in get_player_uuid, there is no query result'))
        return result[0][0]
        
    @classmethod
    def get_player_permissions(cls, nickname: str):
        result = cls.execute_query(f'SELECT * FROM luckperms_user_permissions WHERE uuid = (SELECT uuid from luckperms_players where username = LOWER("{nickname}"))')
        if (not result):
            raise(Exception('Exception in get_player_uuid, there is no query result'))
        permissions = []
        for stroke in result:
            permissions.append({'name': stroke[2], 'enabled': stroke[3], 'expiry': stroke[6]})
        if (permissions == []):
            return None
        return permissions

db = LuckyPermsDatabase()