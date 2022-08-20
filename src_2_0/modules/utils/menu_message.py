import discord

from discord.ui import View
from discord.ext import commands

from .user import GalacticUser

from .paginator.page_stack import PageStack
from .elements.custom_button import CustomButton

from .menu.main_page import MainPage

from config import get_color

from logger import log_debug

class MenuView(View):
    def __init__(self, menu_message, timeout = 120):
        self.menu_message = menu_message
        super().__init__(timeout=timeout)

    async def on_timeout(self):
        await self.menu_message.close('timeout')

class NewMenuMessage(PageStack):
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
        self = NewMenuMessage(bot, user, channel)
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
                self.view.add_item(item)
        # Edit message
        await self.message.edit(embed=embed, view=self.view)
        if (attachment != None):
            await self.message.add_files(attachment)
    
    async def return_button_callback(self):
        log_debug('Return button clicked')
        if (len(self.stack) > 1):
            self.previous()
            await self.update()

    async def close_button_callback(self):
        log_debug('Close button clicked')
        await self.close('closed by user')

    def get_return_button(self):
        return self.return_button
    
    def get_close_button(self):
        return self.close_button
