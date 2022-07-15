import os
import json

import discord

from logger import log_error

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
            log_error(f'While sending Embeded Message from JSON. There is no replace_dict.\n Missing keys: {keys}')
            return None
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
        log_error(f'Exception while sending Embeded Message from JSON. String:\n{message_string}')
        return None
    # Sending embeded message to discord.channel
    return discord.Embed.from_dict(message_dict)