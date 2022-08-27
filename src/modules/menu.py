import re
from xml.dom.minidom import parseString

# Discord
import discord
from discord.ui import View
from discord.ext import commands

# Default
from logger import log_error, log_info, log_debug
from config import get_color, config

# My Classes
from .utils.user import GalacticUser, Player

# Datab Sources
from .utils.database.players_db import PlayersDatabase

# Libraries
from .utils.mc_skins import SkinProvider

# Elements
from .utils.paginator.page import Page
from .utils.paginator.page_stack import PageStack
from .utils.elements.custom_button import CustomButton
from .utils.elements.dropdown import Dropdown

# Enums
from .utils.enums.mc_settings import McSettings

########################################
##           SETTINGS PAGE            ##
########################################
class AccountSettingsPage(Page):
    def __init__(self, menu_message, player: Player, settings_type):
        self.player: Player = player
        self.menu_message = menu_message
        self.settings_type = settings_type
        super().__init__()

    @classmethod
    async def create(cls, menu_message, player, settings_type):
        self = AccountSettingsPage(menu_message, player, settings_type)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        toggle_button = None
        dropdown = None
        if (type(self.settings_type.value['variants'][0]['key']) == int):
            if self.player.settings[self.settings_type.name]:
                label = 'Отключить'
                color = discord.ButtonStyle.red
            else:
                label = 'Включить'
                color = discord.ButtonStyle.green
            toggle_button = CustomButton(color, label)
            toggle_button.set_callback(self.toggle_button_callback)
        else: 
            options = []
            for variant in self.settings_type.value['variants']:
                if (variant['key'] == self.player.settings['tab_type']):
                    options.append({'label': variant['name'], 'description': variant['description'], 'emoji': variant['emoji'], 'default':1})
                else:
                    options.append({'label': variant['name'], 'description': variant['description'], 'emoji': variant['emoji']})
            dropdown = Dropdown(self.menu_message, "Выберите вид TAB'a на сервере", options)
            dropdown.set_callback(self.dropdown_callback)

        if (dropdown != None):
            self.view_items.append(dropdown)
        self.view_items.append(self.menu_message.get_return_button())
        if (toggle_button != None):
            self.view_items.append(toggle_button)
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        # If settings value True/False
        if (type(self.settings_type.value['variants'][0]['key']) == int):
            if (self.player.settings[self.settings_type.name]):
                embed.color = get_color('success')
                enabled_str = 'Вкл.'
            else:
                embed.color = get_color('closed')
                enabled_str = 'Откл.'
            embed.title = f"{self.settings_type.value['name']} ({enabled_str})"
            embed.description = f"{self.settings_type.value['emoji']} **{self.settings_type.value['description']}**"
            if ('image' in self.settings_type.value):
                embed.set_image(url=self.settings_type.value['image'])
        # If settings value str
        else:
            embed.title = f"{self.settings_type.value['name']}"
            embed.color = get_color(self.player.settings['tab_type'])
            embed.description = f"{self.settings_type.value['emoji']} **{self.settings_type.value['description']}**"
            for variant in self.settings_type.value['variants']:
                if variant['key'] == self.player.settings[self.settings_type.name]:
                     if ('image' in variant):
                        embed.set_image(url=variant['image'])
        self.embed = embed

    async def toggle_button_callback(self):
        log_debug('toggle button callback')
        if self.player.settings[self.settings_type.name]:
            self.player.set_settings_value(self.settings_type.name, 0)
            self.player.settings[self.settings_type.name] = 0
        else:
            self.player.set_settings_value(self.settings_type.name, 1)
            self.player.settings[self.settings_type.name] = 1
        self.embed = None
        self.view_items.clear()
        self.create_embed()
        self.create_view_items()
        await self.menu_message.update()

    async def dropdown_callback(self, arg: str):
        for tab_type in self.settings_type.value['variants']:
            if (tab_type['name'] == arg):
                self.player.set_settings_value('tab_type', tab_type['key'])
                self.player.settings['tab_type'] = tab_type['key']
                self.embed = None
                self.view_items.clear()
                self.create_embed()
                self.create_view_items()
                await self.menu_message.update()
                return
        raise ValueError(f'There is no settings with name: {arg}')
        

########################################
##       SELECTOR SETTINGS PAGE       ##
########################################
class AccountSelectorSettingsPage(Page):
    def __init__(self, menu_message, player: Player):
        self.player: Player = player
        self.menu_message = menu_message
        self.settings_types = []
        super().__init__()

    @classmethod
    async def create(cls, menu_message, player):
        self = AccountSelectorSettingsPage(menu_message, player)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Create dropdown
        options = []

        self.settings_types.append(McSettings.get('quick_auth'))
        self.settings_types.append(McSettings.get('join_notify'))
        self.settings_types.append(McSettings.get('tab_type'))

        for settings_type in self.settings_types:
            # if(settings_type.name == 'quick_auth'):
            #     options.append({'label': settings_type.value['name'], 'description': settings_type.value['description'], 'emoji': settings_type.value['emoji'], 'default': True})
            # else:
            options.append({'label': settings_type.value['name'], 'description': settings_type.value['description'], 'emoji': settings_type.value['emoji']})

        dropdown = Dropdown(self.menu_message, 'Настройки аккаунта', options)
        dropdown.set_callback(self.dropdown_callback)
        # Add to view items
        self.view_items.append(dropdown)
        self.view_items.append(self.menu_message.get_return_button())
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        # page: Page = await AccountSettingsPage.create(self.menu_message, self.player, McSettings.get('quick_auth'))
        # self.embed = page.get_embed()
        embed = discord.Embed()
        # Title
        embed.color = get_color('neutral')
        embed.description = 'Выберите интересующие вас настройки:'
        self.embed = embed

    async def dropdown_callback(self, arg: str):
        for type in self.settings_types:
            if (arg == type.value['name']):
                # next_page: Page = await AccountSettingsPage.create(self.menu_message, self.player, type)
                # self.embed = next_page.get_embed()
                # await self.menu_message.update()
                await self.menu_message.switch_page(await AccountSettingsPage.create(self.menu_message, self.player, type))
                return
        raise ValueError(f'There is no settings with name: {arg}')

########################################
##           ACCOUNT PAGE             ##
########################################
class AccountPage(Page):
    def __init__(self, menu_message, player: Player):
        self.player: Player = player
        self.menu_message = menu_message
        super().__init__()

    @classmethod
    async def create(cls, menu_message, player):
        self = AccountPage(menu_message, player)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Creating accounts button
        settings_button = CustomButton(discord.ButtonStyle.green, 'Настройки')
        settings_button.set_callback(self.settings_button_callback)
        # Append item list
        self.view_items.append(self.menu_message.get_return_button())
        self.view_items.append(settings_button)
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        galactic_user = self.menu_message.galactic_user
        if (self.player.head == None):
            self.player.head = SkinProvider.get_head(self.player.realname)
        self.attachment = discord.File(self.player.head, filename='image.png')
        embed.set_thumbnail(url="attachment://image.png")
        # Title
        active = '(Активен)' if galactic_user.status.name == 'access' and self.player.has_access == 1 else '(Неактивен)'
        embed.title = f"{self.player.realname} {active}"
        # Color
        embed.color = get_color('neutral')
        # Base information field
        role_name = f"{self.player.groups[0].value['name']} {self.player.groups[0].value['emoji']}"
        reg_date = self.player.reg_date.strftime('%Y-%m-%d')
        embed.add_field(name='Основная информация', value=f"Роль: `{role_name}`\nНаиграно: `IN_DEV`\nЗарегистрирован: `{reg_date}`", inline=1)
        {'name': 'Администратор', 'emoji': '🟥', 'weight': 100, 'primary': 1}
        group_text = ''
        for group in self.player.groups:
            group_text += f"`{group.value['name']} {group.value['emoji']}`\n"
        embed.add_field(name='Группы', value=group_text, inline=1)
        self.embed = embed
    
    async def settings_button_callback(self):
        log_debug('settings button callback')
        await self.menu_message.switch_page(await AccountSelectorSettingsPage.create(self.menu_message, self.player))


########################################
##      ACCOUNT SELECTION PAGE        ##
########################################
class AccountSelectionPage(Page):
    def __init__(self, menu_message):
        self.menu_message = menu_message
        super().__init__()

    @classmethod
    async def create(cls, menu_message):
        self = AccountSelectionPage(menu_message)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Create dropdown
        options = []
        galactic_user: GalacticUser = self.menu_message.galactic_user
        for player in galactic_user.players:
            options.append({'label': player.realname, 'description': player.groups[0].value['name'], 'emoji': player.groups[0].value['emoji']})
        dropdown = Dropdown(self.menu_message, 'Мои аккаунты', options)
        dropdown.set_callback(self.dropdown_callback)
        # Add to view items
        self.view_items.append(dropdown)
        self.view_items.append(self.menu_message.get_return_button())
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        # Title
        embed.color = get_color('neutral')
        embed.description = 'Пожалуйста, выберите аккаунт с которым вы хотите работать:'
        self.embed = embed

    async def dropdown_callback(self, realname: str):
        log_debug(f'Dropdown ckicked {realname}')
        username = realname.lower()
        for player in self.menu_message.galactic_user.players:
            if (player.username == username):
                await self.menu_message.switch_page(await AccountPage.create(self.menu_message, player))
                return


########################################
##             MAIN PAGE              ##
########################################
class MainPage(Page):
    def __init__(self, menu_message):
        self.menu_message = menu_message
        super().__init__()

    @classmethod
    async def create(cls, menu_message):
        self = MainPage(menu_message)
        self.create_embed()
        self.create_view_items()
        return self

    def create_view_items(self):
        # Creating accounts button
        accounts_button = None
        players: list[Player] = self.menu_message.galactic_user.players
        if (len(players) > 0):
            if (len(players) == 1):
                accounts_button = CustomButton(discord.ButtonStyle.green, players[0].realname)
            else:
                accounts_button = CustomButton(discord.ButtonStyle.green, 'Аккаунты')
            accounts_button.set_callback(self.accounts_button_callback)
        # Append item list
        self.view_items.append(self.menu_message.get_return_button())
        if (accounts_button != None):
            self.view_items.append(accounts_button)
        self.view_items.append(self.menu_message.get_close_button())
    
    def create_embed(self):
        embed = discord.Embed()
        galactic_user: GalacticUser = self.menu_message.galactic_user
        # Title
        embed.title = 'Меню пользователя'
        # Description
        status = f"{galactic_user.status.value['name']} {galactic_user.status.value['emoji']}" 
        status_description = galactic_user.status.value['description']
        inviter_id = galactic_user.inviter_id
        joined = galactic_user.user.joined_at.strftime('%Y-%m-%d %H:%M')
        embed.description = f'Статус верификации: `{status}`\nОписание: `{status_description}`\n\nПригласивший: <@{inviter_id}>\nПрисоединился: `{joined}`'
        # Color
        embed.color = get_color('neutral')
        # Picture
        if (self.menu_message.user.avatar == None):
            embed.set_thumbnail(url='https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702')
        else:
            embed.set_thumbnail(url=self.menu_message.user.avatar.url)
        # Fields
        # players: list[Player] = galactic_user.players
        # for player in players:
        #     active = 'да' if galactic_user.status.name == 'access' and player.has_access == 1 else 'нет'
        #     role_name = f"{player.groups[0].value['name']} {player.groups[0].value['emoji']}"
        #     date = player.reg_date.strftime('%Y-%m-%d')
        #     embed.add_field(name=player.realname, inline=1, value=f'Активен: `{active}`\nРоль: `{role_name}`\nНаиграно: `IN_DEV`\nЗарегистрирован: `{date}`')
        self.embed = embed
    
    async def accounts_button_callback(self):
        if (len(self.menu_message.galactic_user.players) == 1):
            await self.menu_message.switch_page(await AccountPage.create(self.menu_message, self.menu_message.galactic_user.players[0]))
        else:
            await self.menu_message.switch_page(await AccountSelectionPage.create(self.menu_message))
            log_debug('accounts button callback')


########################################
##             MENU VIEW              ##
########################################
class MenuView(View):
    def __init__(self, menu_message, timeout = 120):
        self.menu_message = menu_message
        super().__init__(timeout=timeout)

    async def on_timeout(self):
        await self.menu_message.close('timeout')


########################################
##            MENU MESSAGE            ##
########################################
class MenuMessage(PageStack):
    def __init__(self, bot: commands.Bot, user: discord.user, channel: discord.channel):
        self.closed = 0                             # Is message closed

        self.bot = bot                              # Discord bot
        self.user = user                            # Interaction user
        self.channel = channel                      # Channel where invoked

        self.galactic_user: GalacticUser = None     # Database user

        self.message: discord.Message               # Message with menu

        self.view = MenuView(self)                  # Menu-View (Interactive part)

        self.return_button: CustomButton = None     # Return button
        self.close_button: CustomButton = None      # Exit button

        super().__init__()

    @classmethod
    async def create(cls, bot: commands.Bot, user: discord.user, channel: discord.channel):
        '''
            Create and send new MenuMessage
        '''
        self = MenuMessage(bot, user, channel)
        # Create return button
        self.return_button = CustomButton(discord.ButtonStyle.gray, label='Назад')
        self.return_button.set_callback(self.return_button_callback)
        # Create close button
        self.close_button = CustomButton(discord.ButtonStyle.red, label='Закрыть')
        self.close_button.set_callback(self.close_button_callback)
        # Create user
        self.galactic_user = GalacticUser(self.bot.get_member(self.user.id))
        # MainPage creation
        self.add(await MainPage.create(self))
        # Send message
        await self.send()
        return self
    
    async def switch_page(self, page):
        if (type(page) != type(self.stack[-1])):
            self.add(page)
            await self.update()

    async def close(self, reason: str = None):
        if (not self.closed):
            self.closed = 1
            # Clear object variables
            self.view.clear_items()
            self.view.stop()
            self.stack.clear()
            # Clear discord message
            await self.message.remove_attachments()
            # Edit message to closed
            embed = discord.Embed()
            embed.color = get_color('neutral')
            reason = '' if reason == None else ': `' + reason + '`'
            embed.description = f'Работа меню завершена{reason}'
            await self.message.edit(embed = embed, view = None)
            # Remove message from list
            del self.bot.get_cog('MenuCog').menu_messages[str(self.user.id)]
            log_debug(f'Menu was closed with reason{reason}')
    
    async def send(self):
        '''
            Send new menu_message
        '''
        # Switch page
        page = self.get_last()
        embed = page.get_embed()
        attachment = page.get_attachment()
        if (page.get_view_items() != None):
            for item in page.get_view_items():
                self.view.add_item(item)
        self.message = await self.channel.send(embed=embed, view=self.view)
        if (attachment != None):
            await self.message.add_files(attachment)

    async def update(self):
        # Clear message
        await self.message.remove_attachments()
        self.view.clear_items()
        # Switch page
        page = self.get_last()        
        embed = page.get_embed()
        attachment = page.get_attachment()
        if (page.get_view_items() != None):
            for item in page.get_view_items():
                item.reset()
                self.view.add_item(item)
        # Edit message
        await self.message.edit(embed=embed, view=self.view)
        if (attachment != None):
            await self.message.add_files(attachment)
    
    async def return_button_callback(self):
        log_debug('Return button clicked')
        if (len(self.stack) > 1):
            self.previous()
            if (type(self.get_last()) == AccountPage):
                self.get_last().create_embed()
            await self.update()

    async def close_button_callback(self):
        log_debug('Close button clicked')
        await self.close('closed by user')

    def get_return_button(self):
        return self.return_button
    
    def get_close_button(self):
        return self.close_button



########################################
##              MENU COG              ##
########################################
class MenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.menu_messages = {}

    @commands.Cog.listener()
    async def on_ready(self):
        log_info("Menu Module successfully loaded!")

    @commands.hybrid_command(name='head')
    async def head_command(self, ctx, username:str = None, hidden=True):
        username = username.lower()
        if (PlayersDatabase.authme_check_nickname(username)):
            with open(SkinProvider.get_head(username), 'rb') as head_image:
                picture = discord.File(head_image)
                await ctx.send(file=picture)
        else:
            raise ValueError(f'Такого игрока нет на сервере: {username}')

    @head_command.error
    async def head_command_error(self, ctx, error):
        await ctx.send(f'Ошибка: {error}')

    @commands.hybrid_command(name='test_1')
    @commands.is_owner() 
    async def test_command(self, ctx, mem:str = None):
        if (mem == None):
            mem = ctx.author
        else:
            nums = re.findall(r'\b\d+\b', mem)
            print(nums)
            try:
                mem = self.bot.get_member(int(nums[0]))
            except Exception as e:
                print(e)
                ctx.send('Error')
        print(type(mem))
        galactic_user = GalacticUser(self.bot.get_member(mem.id))
        try:
            string = ''
            string += f'user: {galactic_user.user.mention}\n'
            string += f'inviter: <@{galactic_user.inviter_id}>\n'
            string += f'\n'
            string += f'invited_players: {galactic_user.invited_players}\n'
            string += f'invited_users: {galactic_user.invited}\n'
            string += f'\n'
            string += f'status: {galactic_user.status.name}\n'
            string += f'icon: {galactic_user.status.value["emoji"]}\n'
            string += f'name: {galactic_user.status.value["name"]}\n'
            string += f'description: {galactic_user.status.value["description"]}\n'
            string += f'\n'
            for players in galactic_user.players:
                string += f'**{players.realname}**\n'
                string += f'last_ip: {players.last_ip}\n'
                string += f'last_login: {players.last_login.strftime("%Y-%m-%d %H:%M")}\n'
                string += f'reg_date: {players.reg_date.strftime("%Y-%m-%d %H:%M")}\n'
                string += f'is_logged: {players.is_logged}\n'
                string += f'has_access: {players.has_access}\n'
                string += f'*groups:* \n'
                for group in players.groups:
                    string += f'group: `{group.name} {group.value["emoji"]} {group.value["weight"]} {group.value["primary"]}`\n'
                string += f'settings: quick_auth({players.settings["quick_auth_enabled"]}) join_notify({players.settings["join_notify_enabled"]})\n'
            await ctx.send(string)
        except Exception as e:
            print(e)
    
    @commands.hybrid_command(name='menu')
    @commands.dm_only()
    async def menu_command(self, ctx):
        try:
            # Close opened user's menu if exist
            if str(ctx.author.id) in self.menu_messages.keys():
                await self.menu_messages[str(ctx.author.id)].close('another menu openned')
            # Open new menu
            menu_message = await MenuMessage.create(self.bot, ctx.author, ctx.channel)
            self.menu_messages[str(ctx.author.id)] = menu_message
        except Exception as e:
            log_error(e)
            raise(e)
    
    @menu_command.error
    async def menu_command_error(self, ctx, error):
        print(type(error))
        if (type(error) == commands.errors.PrivateMessageOnly):
            await self.bot.send_simple_embed(ctx.channel, title='Ошибка!', description=f'Данная команда может быть использована только в личных сообщениях.', color='error')
        else:
            await self.bot.send_simple_embed(ctx.channel, title='Непредвиденная ошибка!', description=f'Пожалуйста, обратитесь к администратору <@222746438814138368>, чтобы решить эту проблему.', color='error')

    async def close_all_menu(self):
        for key in self.menu_messages:
            await self.menu_messages[key].close('MODULE RELOADED BY OWNER')

async def setup(bot):
    await bot.add_cog(MenuCog(bot))