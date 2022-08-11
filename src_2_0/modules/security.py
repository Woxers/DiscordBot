import discord
from discord.ext import commands
from datetime import datetime

from logger import log_error, log_info, log_debug
from config import get_color, config
from discord.ui import Button, View

from database import Database

import ipinfo

class AuthMessage():
    # View with auth buttons
    class AuthView(View):
        def __init__(self, auth_message):
            super().__init__(timeout=120)
            self.auth_message = auth_message

        @discord.ui.button(label='Авторизовать', style=discord.ButtonStyle.green, emoji='🔓')
        async def on_auth_button(self, interaction, button):
            self.stop()
            self.timeout = 1
            await self.auth_message.delete_quick_auth_message()
            log_debug('Login button clicked!')

        @discord.ui.button(label='Это не я!', style=discord.ButtonStyle.red, emoji='🔒')
        async def on_not_me_button(self, interaction, button):
            self.stop()
            self.timeout = 1
            await self.auth_message.delete_quick_auth_message()
            log_debug('Not Me button clicked!')

        async def on_timeout(self):
            log_debug('AuthView Timeout')
            self.stop()
            await self.auth_message.delete_quick_auth_message()

    # Ipinfo
    ipinfo_handler = None

    def __init__(self, bot):
        if (AuthMessage.ipinfo_handler == None):
            AuthMessage.ipinfo_handler = ipinfo.getHandler(config['ipinfo']['token'], cache_options={'ttl':30, 'maxsize': 4096})
        
        self.bot = bot
        
        self.channel = None                 # Channel where to send message
        self.auth_message = None            # Message with information
        self.quick_auth_message = None      # Message with buttons

        self.color = None

        self.nickname = None                # Username |
        self.ip = None                      # IP address of user |
        self.location = None                # IP Location |
        self.auth_status = False            # Status of authentification |
        self.closed_status = False          # Connection to proxy status |
        self.event_logs = []                # String events

        self.view = self.AuthView(self)

    # Set ip and get location
    def set_ip(self, ip_address):
        ip_info = AuthMessage.ipinfo_handler.getDetails(ip_address)
        self.ip = ip_address
        self.location = f'{ip_info.country_name}, {ip_info.city}'

    # Add event to logs
    def add_event_log(self, emoji: str, level: int, text: str, unix_timestamp: int):
        string = ''
        if (level == 1):
            string += '``🔶`` ``'
        elif (level == 2):
            string += '``🔷`` ``'
        else:
            raise ValueError(f'There is no level - {level}')
        if (emoji != ''):
            string += f'{emoji}`` ``'
        string += datetime.utcfromtimestamp(unix_timestamp / 1000).strftime('[%H:%M:%S]') + ' '
        string += text
        string += '``'
        self.event_logs.append(string)

    # Switch auth_status to True
    def login(self):
        self.auth_status = True

    # Switch closed_status to True
    def close(self):
        self.closed_status = True
    
    # Build keys for embed message
    def build_message_keys(self):
        # Check all fields
        if (self.nickname == None):
            raise ValueError('nickname is not defined!')
        if (self.ip == None):
            raise ValueError('ip is not defined!')
        if (self.location == None):
            raise ValueError('location is not defined!')
        if (len(self.event_logs) == 0):
            raise ValueError('event_logs is empty!')
        if (self.color == None):
            raise ValueError('color is not defined!')
        # Build dictionary
        dt = {}
        dt['COLOR'] = self.color
        dt['NICKNAME'] = self.nickname
        dt['IP'] = self.ip
        dt['LOCATION'] = self.location
        dt['AUTH_STATUS'] = 'Да' if self.auth_status else 'Нет' 
        dt['CLOSED_STATUS'] = 'Да' if self.closed_status else 'Нет'
        dt['LOGS'] = ''
        for event_log in self.event_logs:
            dt['LOGS'] += f'{event_log} \\n'
        return dt

    # Send quick auth
    async def send_quick_auth_message(self):
        if (self.quick_auth_message == None):
            self.quick_auth_message = await self.bot.send_simple_embed(self.channel, title= 'Quick Auth', description= 'У вас есть `две минуты`, чтобы воспользоваться быстрой авторизацией. \nПосле сообщение будет удалено! \n\n > **Не работает! Функция находится в разработке!**', color = 'neutral', view = self.view)
        else:
            log_error('Quick Auth Message already exists!')
    
    # Delete quick auth message
    async def delete_quick_auth_message(self):
        if (self.quick_auth_message != None):
            await self.quick_auth_message.delete()
            self.quick_auth_message = None

    # Send new or update existing auth message
    async def send_auth_message(self):
        try:
            dt = self.build_message_keys()
        except ValueError as e:
            log_error(e)
        if (self.auth_message == None):
            self.auth_message = await self.bot.send_json_embed(self.channel, 'security/player_connected.txt', replace_dict=dt)
        else:
            await self.bot.send_json_embed(message = self.auth_message, message_path = 'security/player_connected.txt', replace_dict=dt)

class SecurityCog(commands.Cog):
    last_bungee_event = None
    last_auth_event = None
    events_limit = 5
    messages = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.last_bungee_event = Database.execute_query('SELECT get_last_bungee_event_id()')[0][0]
        self.last_auth_event = Database.execute_query('SELECT get_last_auth_event_id()')[0][0]
        log_info("Security Module successfully loaded!")

    @commands.command(name='test-buttons')
    @commands.is_owner() 
    async def test_buttons(self, ctx, *args):
        button1 = Button(label='Авторизовать', style=discord.ButtonStyle.green, emoji='🔓')
        button2 = Button(label='Это не я!', style=discord.ButtonStyle.red, emoji='🔒')

        async def button_callback(interaction):
            await interaction.response.edit_message(interaction)

        button1.callback = button_callback
        button2.callback = button_callback

        view = View()
        view.add_item(button1)
        view.add_item(button2)
        await ctx.send("Hi!", view=view)

    async def process_mc_events(self):
        # Get events from database
        bungee_events = Database.execute_query(f'SELECT * FROM bungee_events WHERE id > {self.last_bungee_event} LIMIT {str(self.events_limit)}')
        if (len(bungee_events) > 0):
            auth_events = Database.execute_query(f'SELECT * FROM auth_events WHERE id > {self.last_auth_event} and unix_timestamp < {bungee_events[-1][6]}')
        else:
            auth_events = Database.execute_query(f'SELECT * FROM auth_events WHERE id > {self.last_auth_event}')
            if (len(auth_events) > 0):
                bungee_events = Database.execute_query(f'SELECT * FROM bungee_events WHERE id > {self.last_bungee_event} and unix_timestamp < {auth_events[-1][4]}')

        # Sort events by unix_timestamp
        events = []
        i = 0
        j = 0
        while (i < len(bungee_events) or j < len(auth_events)):
            if (i < len(bungee_events) and j == len(auth_events)):
                events.append(bungee_events[i])
                i += 1
            elif (i == len(bungee_events) and j < len(auth_events)):
                events.append(auth_events[j])
                j += 1
            elif (bungee_events[i][6] < auth_events[j][4]):
                events.append(bungee_events[i])
                i += 1
            else:
                events.append(auth_events[j])
                j += 1
        
        # Process events
        for event in events:
            db_user = Database.get_user_by_nickname(event[3])
            if (db_user == None):
                continue
            member = self.bot.guild.get_member(db_user['id'])
            if (member == None):
                continue
            channel = member.dm_channel
            if (channel == None):
                channel = await member.create_dm()

            # channel = self.bot.guild.get_channel(978722988893544478)

            if len(event) > 5:
            # Handle Bungee Event
                if (event[2] == 'PlayerConnectEvent'):
                    if (not Database.execute_query(f'select player_id from session_logs where id = {event[1]}')[0][0] == None):
                        auth_message = AuthMessage(self.bot)
                        auth_message.color = get_color('neutral')
                        auth_message.channel = channel
                        auth_message.set_ip(event[5])
                        auth_message.nickname = Database.execute_query(f'select realname from authme where username = "{event[3]}"')[0][0]
                        auth_message.add_event_log('', 1, 'Присоединился к серверу!', event[6])
                        await auth_message.send_auth_message()
                        await auth_message.send_quick_auth_message()
                        self.messages[f'{str(event[1])}'] = auth_message
                elif (event[2] == 'PlayerDisconnectEvent'):
                    if (str(event[1]) in self.messages.keys()):
                        auth_message = self.messages[str(event[1])]
                        auth_message.add_event_log('', 1, 'Вышел с сервера!', event[6])
                        auth_message.close()
                        await auth_message.send_auth_message()
                        await auth_message.delete_quick_auth_message()
                        del self.messages[str(event[1])]
                    else:
                        log_error(f'Cannot close Bungee Event \n {event}')
                else:
                    log_error(f'Cannot handle Bungee Event \n {event}')
            else:
            # Handle Auth Event
                if (str(event[1]) in self.messages.keys()):
                    if (event[2].startswith('onLogin')):
                        auth_message = self.messages[str(event[1])]
                        auth_message.color = get_color('success')
                        auth_message.add_event_log('🔓', 2, 'Успешно авторизован', event[4])
                        auth_message.login()
                        if (event[2].endswith('ChangedIp')):
                            auth_message.color = get_color('changed_ip')
                            auth_message.add_event_log('⚠️', 2, 'Изменен ip адрес!', event[4])
                        await auth_message.delete_quick_auth_message()
                        await auth_message.send_auth_message()
                    elif (event[2].startswith('onFailedLogin')):
                        auth_message = self.messages[str(event[1])]
                        auth_message.color = get_color('error')
                        auth_message.add_event_log('🚫', 2, 'Неудачная попытка входа в аккаунт!', event[4])
                        await auth_message.send_auth_message()
                else:
                    log_error(f'Cannot handle Auth Event \n {event}')
        
        self.last_bungee_event += len(bungee_events)
        self.last_auth_event += len(auth_events)
        
async def setup(bot):
    await bot.add_cog(SecurityCog(bot))