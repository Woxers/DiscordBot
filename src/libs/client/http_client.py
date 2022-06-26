import requests
import json

import datetime
import threading
import time

import urllib3

urllib3.disable_warnings()

host = '51.83.146.19'
port = '25598'
token = 'X5BVWKoIrHX7NVMxl24AjjrD8WdVmhe9'

url = 'https://' + host + ':' + port + '/'

# Singleton
class McApiClient:
    __instance = None
    __player_joined_callbacks = []
    __player_left_callbacks = []
    __server_unavaible_callbacks = []
    __server_started_callbacks = []

    players_list = []
    server_status = False

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(McApiClient, cls).__new__(cls)
            return cls.__instance

    def online_method(cls):
        while(True):
            try:
                r = requests.get(f'{url}online?token={token}', verify=False)
                jsonn = json.loads(r.text)

                new_players_list = []
                for players in jsonn['players_list']:
                    new_players_list.append(players['nickname'])

                players_count(jsonn['total'])
                players_list = []
                for players in jsonn['players_list']:
                    players_list.append(players['nickname'])
                print_players(players_list)
            except Exception as e:
                print(e)
                time.sleep(1.5)
                pass
            time.sleep(0.5)

def function():
    print('function touched')

def mc_server_info():
    while(True):
        try:
            r = requests.get(f'{url}online?token={token}', verify=False)
            jsonn = json.loads(r.text)
            players_count(jsonn['total'])
            players_list = []
            for players in jsonn['players_list']:
                players_list.append(players['nickname'])
            print_players(players_list)

        except Exception as e:
            print(e)
            pass
        time.sleep(1)

def players_count(count):
    print(f'На сервере сейчас: {count}')

def print_players(players_list):
    print(f'Игроки: {players_list}')


th = threading.Thread(target=mc_server_info)
th.run()


