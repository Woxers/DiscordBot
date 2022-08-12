import discord

from discord.ui import Button

from logger import log_debug

class ReturnButton(Button):
    def __init__(self, menu_message):
        self.clicked = 0
        self.menu_message = menu_message
        super().__init__(style=discord.ButtonStyle.grey, label='Назад')

    async def callback(self, interaction: discord.Interaction):
        if (not self.clicked):
            self.clicked = 1
            log_debug('ReturnButton callback')
            if (not await self.menu_message.previous_page()):
                self.disabled = True
                await self.menu_message.update()
            await interaction.response.defer()
        else:
            log_debug('AccountsButton was clicked before...')