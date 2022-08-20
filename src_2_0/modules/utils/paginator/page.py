import discord

class Page():
    '''
        `attachments: discord.File = []` - Images, files\n
        `view_items: discord.ui.* = []` - Buttons, Selections and other\n
        `embed: discord.Embed` - Discord embed
    '''
    def __init__(self):
        self.attachment: discord.File = None
        self.view_items = []
        self.embed: discord.Embed = None
    
    @classmethod
    async def create(cls):
        self = Page()
        return self
    
    def get_attachment(self):
        return self.attachment
    
    def get_view_items(self):
        if (len(self.view_items) == 0):
            return None
        return self.view_items
    
    def get_embed(self):
        return self.embed