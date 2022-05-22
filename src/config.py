import json
import os.path

# Singleton 
class Config():
    __instance = None
    __json_string = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Config, cls).__new__(cls)
            path = os.getcwd() + '\data\settings.json'
            with open(path, 'r', encoding='utf-8') as settings:
                cls.__json_string=json.load(settings)
            settings.close()
            print("New Config Object created!")

        return cls.__instance

    @classmethod
    def get(cls, settingsType, key):
        # if cls.__instance is None: 
        #     cls.__new__(cls)
        return cls.__json_string[settingsType][key]

    @classmethod
    def set(cls, settingsType, key):
        # if cls.__instance is None: 
        #     cls.__new__(cls)
        cls.__json_string['server']['auto_role'] = '4e'
        cls.update()

    @classmethod
    def update(cls):
        # if cls.__instance is None: 
        #     cls.__new__(cls)
        path = os.getcwd() + '\data\settings.json'
        with open(path, 'w', encoding='utf-8') as settings:
            json.dump(cls.__json_string, settings, ensure_ascii=False, indent=4)
        settings.close()

config = Config()