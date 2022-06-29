import os.path

import logging
import datetime

from sys import platform

from config import Config
from sys import platform

# Инициализация логирования
# path = '/home/aptem/VScodeRep/GalacticManager/src/logs/' + 'latest.log'
# path = os.getcwdb().decode("utf-8") + '\logs\latest.log'

path = ''

if platform == "linux" or platform == "linux2":
    path = '/home/testuser/GalacticManager/src/logs/' + 'latest.log'
else:
    path = os.getcwdb().decode("utf-8") + '\logs\latest.log'

logging.basicConfig(filename=path, filemode='a',format='[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=20)
logging.info('Start logging')

os.getcwdb()