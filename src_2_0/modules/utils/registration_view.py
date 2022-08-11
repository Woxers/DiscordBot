import discord
from discord.ui import Button, View

class RegistrationView(View):
    def __init__(self, menu_message):
        super().__init__(timeout=120)
        self.menu_message = menu_message
    
    @discord.ui.button(label='Назад', style=discord.ButtonStyle.grey, emoji='⬅️')
    async def on_return_button(self, interaction, button):
        print('Return button clicked')

    @discord.ui.button(label='Зарегистрироваться', style=discord.ButtonStyle.green, emoji='🔱')
    async def on_registration_button(self, interaction, button):
        print('Registration button clicked')