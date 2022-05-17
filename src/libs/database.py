import os.path
import sqlite3
import create_db

class Database:
    __connection = None

    def __init__(self, path):
        print(path)
        if os.path.exists(path):
            print("Exist")
            self.__connection = self.create_connection(path)
        else:
            print("Database not exist, create new one")
            self.__connection = self.create_connection(path)
            self.execute_query(create_db.create_status_table)
            self.execute_query(create_db.create_users_table)
            self.execute_query(create_db.insert_status)

    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connected to SQLite DB")
        except sqlite3.Error as err_string:
            print(f"The error '{err_string}' occured")
        return connection

    def execute_query(self, query):
        cursor = self.__connection.cursor()
        try:
            cursor.execute(query)
            self.__connection.commit()
            return cursor.fetchall()
        except sqlite3.Error as err_string:
            print(f"The error '{err_string}' occurred")

bd = Database("D:/!GitClones/DiscordBot/src/data/users.db")
result = bd.execute_query("SELECT * FROM status")

for a, b in result:
    print(f"Test {a} {b}")
