import os.path

from datetime import datetime

DEBUG_MODE = True

log_path = os.path.dirname(__file__) + '/logs/latest.log'

def write(level: str, message: str):
    with open(log_path, 'a', encoding='utf-8') as file:
        file.write(f'[{datetime.now():%y-%m-%d %H:%M:%S}] [{level}] {message}\n')

# Only if debug mode enabled
def log_debug(message:str):
    if (DEBUG_MODE):
        print(message)
        write('DEBUG', message)

def log_info(message: str):
    print(message)
    write('INFO', message)

def log_warning(message: str):
    print(message)
    write('WARNING', message)

def log_error(message: str):
    print(message)
    write('ERROR', message)

def log_critical(message: str):
    print(message)
    write('CRITICAL', message)

write('INIT', 'Start logging')
