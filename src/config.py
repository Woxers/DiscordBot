import json
import os.path

from sys import platform

# Singleton 
class Config():
    __instance = None
    __json_string = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Config, cls).__new__(cls)

            if platform == "linux" or platform == "linux2":
                path = '/home/testuser/DiscordBot/src/data/settings.json'
            else:
                path = os.getcwdb().decode("utf-8") + '\data\settings.json'
            with open(path, 'r', encoding='utf-8') as settings:
                cls.__json_string=json.load(settings)
            settings.close()

        return cls.__instance

    @classmethod
    def get(cls, settingsType, key):
        return cls.__json_string[settingsType][key]

    @classmethod
    def getColor(cls, color):
        return int(cls.get('embed', f'{color}'), 16)

    @classmethod
    def set(cls, settingsType, key, value):
        cls.__json_string[settingsType][key] = value
        cls.update()

    @classmethod
    def update(cls):
        path = os.getcwd() + '\data\settings.json'
        with open(path, 'w', encoding='utf-8') as settings:
            json.dump(cls.__json_string, settings, ensure_ascii=False, indent=4)
        settings.close()

config = Config()