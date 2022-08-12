import discord
from discord.ui import Button

from logger import log_debug

class CloseButton(Button):
    def __init__(self, menu_message):
        self.clicked = 0
        self.menu_message = menu_message
        super().__init__(style=discord.ButtonStyle.red, label='Закрыть')

    async def callback(self, interaction: discord.Interaction):
        if (not self.clicked):
            self.clicked = 1
            log_debug('CloseButton callback')
            await self.menu_message.close('closed by user')
            await interaction.response.defer()
        else:
            log_debug('AccountsButton was clicked before...')