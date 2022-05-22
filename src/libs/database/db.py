import datetime
import sqlite3
import logging
import os.path
import sys
import re

from tabnanny import check
from time import timezone
from typing import List

logger = logging.getLogger(__name__)

# Connecting sql query for creating a new database and
# connecting path to the directory with the config file
if __name__ == '__main__':
    from create_db_sql import create_status_table
    from create_db_sql import create_users_table
    from create_db_sql import insert_status
    sys.path.append('D:/!GitClones/DiscordBot/src/')
else:
    from .create_db_sql import create_status_table
    from .create_db_sql import create_users_table
    from .create_db_sql import insert_status
    sys.path.append(os.getcwdb()) 
    
from config import Config

# Singleton
class Database:
    __instance = None
    __filePath = Config.get('db', 'path') + Config.get('db', 'name')
    __connection = None
    __statusList = []

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
            if os.path.exists(cls.__filePath):
                logger.info('Database already exist')
                cls.__connection = cls.create_connection()
            else:
                logger.warning('Database not exist, create new one')
                cls.__connection = cls.create_connection()
                cls.execute_query(create_status_table)
                cls.execute_query(create_users_table)
                cls.execute_query(insert_status)
                tempStatusList = cls.execute_query('SELECT Name FROM status')
                for status in tempStatusList:
                    cls.__statusList.append(status[0])
            print('New Database Object created!')
            return cls.__instance

    # Connecting database
    @classmethod
    def create_connection(cls):
        connection = None
        try:
            connection = sqlite3.connect(cls.__filePath)
            logger.info('Connecting to SQLite DB')
        except sqlite3.Error as err_string:
            logger.exception(f'The exception in create_connection occured: {err_string}')
        return connection

    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        cursor = cls.__connection.cursor()
        try:
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except sqlite3.Error as err_string:
            logger.exception(f'The exception in execute_query occured: {err_string}')

    # Add a new user
    @classmethod
    def add_user(cls, id):
        if (id.isnumeric()):
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours = 3)))
            result = cls.execute_query(f''' INSERT INTO users (DiscordID, JoinedDatetime) VALUES ("{id}", "{now}") ''')
            return result
        else:
            logger.eror(f'The error in add_user occured: Invalid User ID: {id}')

    # Is there a user with the specified ID
    @classmethod
    def check_user(cls, id):
        if (id.isnumeric()):
            result = cls.execute_query(f'''SELECT CASE WHEN EXISTS(SELECT Name FROM users where DiscordID = '{id}') = 1 THEN "TRUE" ELSE "FALSE" END''')
            return 1 if (result[0][0] == 'TRUE') else 0
        else:
            logger.eror(f'The error in check_user occured: Invalid User ID: {id}')

    # Set user registration status
    @classmethod
    def set_status(cls, id, status):
        if cls.check_user(id): 
            if status in cls.__statusList:
                cls.execute_query(f''' UPDATE users SET status="{status}" WHERE DiscordID="{id}" ''')
            else:
                print(f'[ERROR] [set_status] Status not exist: {status}')
                return 0
        else:
            logger.eror(f'The error in set_status occured: No player with such ID: {id}')

    # Set user name
    @classmethod
    def set_name(cls, id, name):
        match = re.fullmatch(Config.get('db', 'name_pattern'), name)
        if (match):
            if cls.check_user(id): 
                cls.execute_query(f''' UPDATE users SET Name="{name}" WHERE DiscordID="{id}" ''')
            else:
                logger.eror(f'The error in set_name occured: No player with such ID: {id}')
        else:
            logger.eror(f'The error in set_name occured: Invalid name: {name}')
    
    # Set user nickname
    @classmethod
    def set_nickname(cls, id, nickname):
        match = re.fullmatch(Config.get('db', 'nickname_pattern'), nickname)
        if (match):
            if cls.check_user(id): 
                cls.execute_query(f''' UPDATE users SET Nickname="{nickname}" WHERE DiscordID="{id}" ''')
            else:
                logger.eror(f'The error in set_nickname occured: No player with such ID: {id}')
        else:
            logger.eror(f'The error in set_nickname occured: Invalid nickname: {nickname}')
    
    # Update registration date
    @classmethod
    def update_reg_date(cls, id):
        if cls.check_user(id): 
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours = 3)))
            cls.execute_query(f''' UPDATE users SET RegDatetime="{now}" WHERE DiscordID="{id}" ''')
        else:
            logger.eror(f'The error in update_reg_date occured: No player with such ID: {id}')

db = Database()
