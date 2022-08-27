import os
import json

import discord

from datetime import datetime, timedelta

from config import get_color

from logger import log_error

def make_embed_fields_from_json_file(message_path: str, replace_dict: str = None):
    '''
        Convert JSON file to discord.EmbedProxy

        Arguments
        ---------
            `message_path` - message path in `%PROJECT_FOLDER%/resources/messages`

            `replace_dict` - replace in message `%%key%%` -> `dict['key']`

        Return values
        -------------

            `Array of discord.EmbedProxy` - success

            `None` - failed
    '''
    fields = []
    embed = make_embed_from_json_file(message_path, replace_dict)
    for field in embed.fields:
        fields.append(field)
    return fields

def make_embed_from_json_file(message_path: str, replace_dict: str = None):
    '''
        Convert JSON File to discord.Embed
        
        Arguments
        ---------
            `message_path` - message path in `%PROJECT_FOLDER%/resources/messages`

            `replace_dict` - replace in message `%%key%%` -> `dict['key']`

        Return values
        -------------

            `discord.Embed` - success

            `None` - failed
    '''
    resources_path = os.path.dirname(__file__) + '/resources/messages/'
    path = resources_path + message_path
    # Open file with embed structure
    try:
        with open(path, 'r') as file:
            message_string = file.read()
    except Exception as e:
        log_error(f'Cannot find message_file: {path}')
        return None
    # Get keys from text
    if (not message_string.startswith('{')):
        parts = message_string.partition('\n')
        keys = parts[0].split(', ')
        message_string = parts[2]
        # If there is no replace_dict
        if (replace_dict == None):
            replace_dict = dict()
        # Add to dict default keys if not exist
        if (not replace_dict.get('TIMESTAMP')):
            replace_dict['TIMESTAMP'] = f'{(datetime.now() - timedelta(hours=3)):%Y-%m-%d %H:%M:%S}'
        if (not replace_dict.get('COLOR')):
            replace_dict['COLOR'] = '7506394'
        if (not replace_dict.get('NEUTRAL_COLOR')):
            replace_dict['NEUTRAL_COLOR'] = get_color('neutral')
        if (not replace_dict.get('ERROR_COLOR')):
            replace_dict['ERROR_COLOR'] = get_color('error')
        if (not replace_dict.get('SUCCESS_COLOR')):
            replace_dict['SUCCESS_COLOR'] = get_color('success')
        if (not replace_dict.get('AVATAR_URL')):
            replace_dict['ICON_URL'] = "https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=663&height=663"
        # If keys are missing in replace_dict
        if (keys - replace_dict.keys()):
            log_error(f'While sending Embeded Message from JSON. Keys are missing in replace_dict.\n Missing keys: {keys - replace_dict.keys()}')
            return None
    # Replacing keys(%%key%%) in the text
    if (not replace_dict == None):
        for key, value in replace_dict.items():
            message_string = message_string.replace(f'%%{key}%%', str(value))
    try:
        message_dict = json.loads(message_string)
    except Exception as e:
        log_error(f'Exception while sending Embeded Message from JSON. Json Message:\n{message_string}')
        return None
    # Sending embeded message to discord.channel
    try:
        embed = discord.Embed.from_dict(message_dict)
    except Exception as e:
        log_error(f'Exception while converting Dict to discord.Embed.\nException: {e}\nJson Message:\n{message_string}')
        return None
    return embed