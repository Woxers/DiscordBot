import json
import os.path

from shutil import copyfile

config_path = os.path.dirname(__file__) + '/data/config.json'
example_config_path = os.path.dirname(__file__) + '/resources/config/config.json'

config = None

# Config loader
class ConfigLoader:
    def __init__(self):
        global config
        if os.path.exists(config_path):
            print('[ConfigLoader] Read config file')
            with open(config_path, 'r') as file:
                config = json.load(file)
        else:
            print('[ConfigLoader] Config file doesnt exist, create new one')
            copyfile(example_config_path, config_path)
            with open(config_path, 'r') as file:
                config = json.load(file)

    # Reloads config file
    def reload(self):
        global config
        print('[ConfigLoader] Reloading config')
        with open(config_path, 'r') as file:
            config = json.load(file)

    # Save config
    def save(self):
        global config
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
        file.close()

# Get color from config
def get_color(color_name):
    return int(config['colors'][color_name], 16)

conf = ConfigLoader()