import traceback
import inspect
import os.path

from datetime import datetime

DEBUG_MODE = True

log_path = os.path.dirname(__file__) + '/logs/latest.log'

def write(level: str, message: str):
    with open(log_path, 'a', encoding='utf-8') as file:
        file.write(f'[{datetime.now():%y-%m-%d %H:%M:%S}] [{level}] {message}\n')

# Only if debug mode enabled
def log_debug(message:str):
    if (not DEBUG_MODE):
        return
    try:
        caller_file = inspect.stack()[1][1].split('/')[-1]
    except Exception:
        caller_file = 'unknown'
    print(f'[DEBUG] [{caller_file}] {message}')
    write('DEBUG', f'[{caller_file}] {message}')

def log_info(message: str):
    try:
        caller_file = inspect.stack()[1][1].split('/')[-1]
    except Exception:
        caller_file = 'unknown'
    print(f'[INFO] [{caller_file}] {message}')
    write('INFO', f'[{caller_file}] {message}')

def log_warning(message: str):
    try:
        caller_file = inspect.stack()[1][1].split('/')[-1]
    except Exception:
        caller_file = 'unknown'
    print(f'[WARNING] [{caller_file}] {message}')
    write('WARNING', f'[{caller_file}] {message}')

def log_error(message: str):
    try:
        caller_file = inspect.stack()[1][1].split('/')[-1]
    except Exception:
        caller_file = 'unknown'
    print(f'[ERROR] [{caller_file}] {message}')
    write('ERROR', f'[{caller_file}] {message}')

def log_critical(message: str):
    try:
        caller_file = inspect.stack()[1][1].split('/')[-1]
    except Exception:
        caller_file = 'unknown'
    print(f'[CRITICAL] [{caller_file}] {message}')
    write('CRITICAL', f'[CRITICAL] [{caller_file}] {message}')

write('WARNING', '[logger.py] Start logging!')
