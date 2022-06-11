import os.path

import logging
import datetime

from config import Config
from sys import platform

# Initialize logger
path = '/home/aptem/VScodeRep/DiscordBot/src/logs/' + 'latest.log'

logging.basicConfig(filename=path, filemode='w',format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=20)
logging.info('Start logging')