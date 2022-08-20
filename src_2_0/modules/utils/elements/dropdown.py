import discord

from discord.ui import Select

class Dropdown(Select):
    def __init__(self, menu_message, placeholder, options):
        '''
            options = {'label', 'description', 'emoji'}

            callback - method(realname)
        '''
        self.menu_message = menu_message
        self.callback_function = None
        dropdown_options = []

        for option in options:
            dropdown_options.append(discord.SelectOption(label=option['label'], description=option['description'], emoji=option['emoji']))

        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=dropdown_options)

    def set_callback(self, function):
        '''
            callback - method(realname)
        '''
        self.callback_function = function

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if (self.callback_function != None):
            await self.callback_function(self.values[0])
