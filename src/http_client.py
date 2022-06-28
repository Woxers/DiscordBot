import asyncio
import json
import os
import sys
import threading
import time

import requests

sys.path.append(os.getcwdb()) 
# pyflakes.ignore
import urllib3

# Singleton
class McApiClient:
    urllib3.disable_warnings()

    url = 'https://' + host + ':' + port + '/'

    __instance = None
    __joined_event_handlers = []
    __left_event_handlers = []
    __login_event_handlers = []
    __failed_login_event_handlers = []

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(McApiClient, cls).__new__(cls)
        return cls.__instance
    
    # Start receiving events
    @classmethod
    def start(cls): 
        _thread = threading.Thread(target=cls.receive_mc_events)
        _thread.start()
        print(f'\nMC receiving events started!')

    # Receive events
    @classmethod
    def receive_mc_events(cls):
        while(True):
            print('works')
            try:
                r = requests.get(f'{cls.url}events', verify=False, data={"token":cls.token})
                jsonn = json.loads(r.text)
                if 'events' not in jsonn:
                    raise Exception(f'Reply doesnt contains events: \n {jsonn}')
                for event in jsonn['events']:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    if event['type'] == 'player_joined':
                        loop.run_until_complete(cls.handle_events(cls.__joined_event_handlers, event['value']))
                    elif event['type'] == 'player_quit':
                        loop.run_until_complete(cls.handle_events(cls.__left_event_handlers, event['value']))
                    elif event['type'] == 'player_login':
                        loop.run_until_complete(cls.handle_events(cls.__login_event_handlers, event['value']))
                    elif event['type'] == 'player_failed_login':
                        loop.run_until_complete(cls.handle_events(cls.__failed_login_event_handlers, event['value']))
                    loop.close
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(2)
                pass
    
    # Handle received events
    @classmethod
    async def handle_events(cls, handlers, value):
        for handler in handlers:
            await handler(value)

    # Listener Decorator
    @classmethod
    def listener(cls, event_handler):
        def wrapper():
            if (event_handler.__name__ == 'on_player_join'):
                cls.__joined_event_handlers.append(event_handler)
            elif (event_handler.__name__ == 'on_player_left'):
                cls.__left_event_handlers.append(event_handler)
            elif (event_handler.__name__ == 'on_player_login'):
                cls.__login_event_handlers.append(event_handler)
            elif (event_handler.__name__ == 'on_player_failed_login'):
                cls.__failed_login_event_handlers.append(event_handler)
            else:
                raise Exception(f'Undefined event listener \"{event_handler.__name__}\"')
        return wrapper()

client = McApiClient()

if __name__ == '__main__':
    @client.listener
    async def on_player_join(name):
        print(name + ' joined the server')

    @client.listener
    async def on_player_left(name):
        print(name + ' left the server')

    @client.listener
    async def on_player_login(name):
        print(name + ' logged in')

    @client.listener
    async def on_player_failed_login(name):
        print(name + ' failed login')

