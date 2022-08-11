import discord
from discord.ui import Button, View

from logger import log_debug

class BaseView(View):
    def __init__(self, menu_message):
        super().__init__(timeout=120)
        self.menu_message = menu_message

    @discord.ui.button(label='Аккаунты', style=discord.ButtonStyle.green)
    async def on_accounts_button(self, interaction, button):
        log_debug('Accounts button clicked')
    
    @discord.ui.button(label='Закрыть', style=discord.ButtonStyle.red)
    async def on_close_button(self, interaction: discord.Interaction, button):
        await self.menu_message.close()
        log_debug('Close button clicked')

    async def on_timeout(self):
        log_debug('BaseView Timeout')
        await self.menu_message.close()