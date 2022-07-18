from datetime import datetime
#import time
import pymysql
import logging
import os.path
import sys
import re

logger = logging.getLogger(__name__)

# Connecting sql query for creating a new database and
# connecting path to the directory with the config file
# if __name__ == '__main__':
#     from create_db_sql import create_status_table
#     from create_db_sql import create_users_table
#     from create_db_sql import insert_status
#     sys.path.append('D:/!GitClones/DiscordBot/src/')
# else:
#     from .create_db_sql import create_status_table
#     from .create_db_sql import create_users_table
#     from .create_db_sql import insert_status

sys.path.append(os.getcwdb()) 
from config import Config

# Singleton
class Database:
    __instance = None
    __connection = None
    # __statusList = []
    # __stagesList = []

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
            cls.__connection = cls.create_connection()
            
            # tableList = cls.execute_query(''' SHOW TABLES; ''')
            # if (len(tableList) == 0):
            #     print('There are no tables, create new')
            #     logger.warning('MYSQL Create new tables')
            #     # cls.execute_query(create_status_table)
            #     # cls.execute_query(create_users_table)
            #     # cls.execute_query(insert_status)
            # statusList = cls.execute_query('CALL GetStatuses()')
            # stagesList = cls.execute_query('CALL GetStages()')
            # for status in statusList:
            #     cls.__statusList.append(status[0])
            # for stage in stagesList:
            #     cls.__stagesList.append(stage[0])
            return cls.__instance

    # Refresh connection
    @classmethod
    def reload_connection(cls):
        cls.__connection = cls.create_connection()

    # Connecting database
    @classmethod
    def create_connection(cls):
        connection = None
        try:
            connection = pymysql.connect(host=Config.get('mysql', 'host'), user=Config.get('mysql', 'user'), passwd=Config.get('mysql', 'passwd'), db=Config.get('mysql', 'db'))
            connection.set_charset('utf8')
            logger.info('Connection to MySQL database')
        except pymysql.Error as e:
            logger.critical(f'Cannot connect to Database!\n' + str(e))
            raise SystemExit('Cannot connect to Database!')
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
            logger.exception(f'Exception in execute_query occured, {err_string}')
            return -1

    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        cursor = cls.__connection.cursor()
        try:
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except pymysql.Error as err_string:
            logger.exception(f'The exception in execute_query occured, {err_string}')
            return -1
    
    # Check user
    @classmethod
    def check_user(cls, userId: int):
        res = cls.execute_query(f'SELECT CheckUser({userId})')[0][0]
        return res

    # Add a new user
    @classmethod
    def add_user(cls, userId: int, inviterId: int):
        cls.execute_query(f'CALL AddNewUser({userId}, {inviterId})')

    # Get user
    @classmethod
    def get_user(cls, userId: int):
        dictionary = dict()
        result = cls.execute_query(f'CALL GetUserByID({userId})')[0]
        
        dictionary['DiscordID'] = result[0]
        dictionary['JoinedTimestamp'] = result[1]
        dictionary['Status'] = result[2]
        dictionary['Stage'] = result[3]
        dictionary['InviterID'] = result[4]
        dictionary['ConfirmatorID'] = result[5]
        dictionary['Nickname'] = result[6]
        dictionary['RealNickname'] = result[7]

        return dictionary

    # Set user verification status
    @classmethod
    def set_status(cls, userId: int, status):
        cls.execute_query(f'CALL SetVerificationStatus({userId}, "{status}")')
    
    # Set user interview stage
    @classmethod
    def set_stage(cls, userId: int, stage):
        cls.execute_query(f'CALL SetInterviewStage({userId}, "{stage}")')

    # Check is nickname unique
    @classmethod
    def check_nickname(cls, nickname):
        match = re.fullmatch(Config.get('db', 'nickname_pattern'), nickname)
        nickname = nickname.lower()
        if (match):
            return not cls.execute_query(f'SELECT CheckNickname("{nickname}")')[0][0]
        return 0 

    # Set user nickname
    @classmethod
    def set_nickname(cls, userId: int, nickname):
        cls.execute_query(f'CALL SetNickname({userId}, "{nickname}")')
        return 1

    # Get user id by nickname
    @classmethod
    def get_user_id_by_nickname(cls, nickname):
        return cls.execute_query(f'CALL GetUserIdByNickname("{nickname}")')

    # Get invited not confirmed players
    @classmethod
    def get_invited_not_confirmed(cls):
        return cls.execute_query(f'CALL GetUsersByVerificationStatus("JOINED")')

    # Get all invited players by user
    @classmethod
    def get_invited_by_inviter(cls, userId: int):
        return cls.execute_query(f'CALL GetInvitedByID({userId})')
    
    # Get Count of invited by user
    @classmethod
    def get_invited_count_by_inviter(cls, userId: int):
        return cls.execute_query(f'SELECT GetInvitedCountByID({userId})')[0][0]
    
    # Get all players not confirmed invited by user
    @classmethod
    def get_invited_not_confirmed_by_inviter(cls, userId: int):
        return cls.execute_query(f'CALL GetUsersByVerificationStatusAndInviterID("JOINED", {userId})')

    # Get user status and stage
    @classmethod
    def get_status_and_stage(cls, userId: int):
        dictionary = dict()
        res = cls.execute_query(f'CALL GetVerification({userId})')[0]
        dictionary['status'] = res[0]
        dictionary['stage'] = res[1]
        return dictionary

    # Set confirmator
    @classmethod
    def set_confirmator(cls, userId: int,  confirmatorId: int):
        cls.execute_query(f'CALL SetConfirmatorID({userId}, {confirmatorId})')

    # Delete User
    @classmethod
    def delete_user(cls, userId: int):
        cls.execute_query(f'CALL DeleteUser({userId})')

    # Upd join date (row sql)
    @classmethod
    def upd_joined_date(cls, userId: int, date: datetime.timestamp):
        cls.execute_query(f' UPDATE users SET JoinedTimestamp="{date}" WHERE DiscordID={userId} ')

db = Database()