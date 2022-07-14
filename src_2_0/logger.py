import os.path

from datetime import datetime

log_path = os.path.dirname(__file__) + '/logs/latest.log'

def write(level: str, message: str):
    with open(log_path, 'a', encoding='utf-8') as file:
        file.write(f'[{datetime.now():%y-%m-%d %H:%M:%S}] [{level}] {message}\n')

def log_error(message: str):
    print(message)
    write('ERROR', message)

def log_info(message: str):
    print(message)
    write('INFO', message)

write('INIT', 'Start logging')
