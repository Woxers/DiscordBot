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

    ###################################
    ##             Confirm           ##
    ###################################
    @commands.command(name='confirm', invoke_without_command='True')
    async def confirm(self, ctx, id: int = None):
        print('a')
        print(Database.get_status_and_stage(id))

    ###################################
    ##            GRANT MC           ##
    ###################################
    @commands.command(name='grant-mc', invoke_without_command='True')
    async def grant_mc(self, ctx, id: int = None):
        
        print(Database.get_status_and_stage(id))
    

async def setup(bot):
    await bot.add_cog(VerificationCog(bot))