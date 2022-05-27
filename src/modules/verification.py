import datetime
from typing import List
import discord
import logging

from config import Config
from libs import Database
from discord.ext import commands

logger = logging.getLogger(__name__)

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info('Connecting Verification module')
    
    # Отправляет сообщение о новом игроке
    async def new_player_message(self, member: discord.Member):
        print('invoked')
        user = Database.get_user(member.id)
        stroke = f':small_orange_diamond: Никнейм: {user[0][4]}\n'
        stroke += f':small_orange_diamond: Реально имя: {user[0][3]}\n'
        regDate = user[0][5].split(' ')
        stroke += f':small_orange_diamond: Дата регистрации: {regDate[0]}\n'
        stroke += f':small_blue_diamond: Дискорд: {member.mention}'
        playersChannel = self.bot.get_channel(Config.get('profile', 'channel'))
        embed = discord.Embed(color = Config.getColor('neutral'))
        embed.description = stroke
        embed.set_footer(text='GameSpace#Private \u200b', icon_url="https://media.discordapp.net/attachments/866681575639220255/866681810989613076/gs_logo_1024.webp?width=702&height=702")
        embed.timestamp = timestamp=datetime.datetime.utcnow()
        await playersChannel.send(embed= embed)

def setup(bot):
    bot.add_cog(VerificationCog(bot))