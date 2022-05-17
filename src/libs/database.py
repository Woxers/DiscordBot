import os.path
import sqlite3
import create_db
from sqlite3 import Error

class Database:
    __path = "D:/!GitClones/DiscordBot/src/data/users.db"

    def __init__(self):
        if os.path.exists(self.__path):
            print("Exist")
            self.__connection = create_connection(self.__path)
        else:
            print("Database not exist, create new one")
            self.__connection = create_connection(self.__path)
            execute_query(self.__connection, create_db.create_status_table)
            execute_query(self.__connection, create_db.create_users_table)
            execute_query(self.__connection, create_db.insert_status)

            
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connected to SQLite DB")
    except Error as err_string:
        print(f"The error '{err_string}' occured")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as err_string:
        print(f"The error '{err_string}' occurred")

bd = Database()
