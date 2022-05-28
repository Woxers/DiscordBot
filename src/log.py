import os.path

import logging
import datetime

from config import Config
from sys import platform

# Initialize logger
if platform == "linux" or platform == "linux2":
    path = '/home/DiscordBot/latest.log'
else:
    path = Config.get('log', 'path') + 'latest.log'

logging.basicConfig(filename=path, filemode='w',format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%y-%m-%d %H:%M:%S', encoding='utf-8', level=20)
logging.info('Start logging')