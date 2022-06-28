import os.path

import logging
import datetime

from config import Config
from sys import platform

# Инициализация логирования
# path = '/home/aptem/VScodeRep/DiscordBot/src/logs/' + 'latest.log'
path = os.getcwdb().decode("utf-8") + '\logs\latest.log'

logging.basicConfig(filename=path, filemode='a',format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=20)
logging.info('Start logging')

os.getcwdb()