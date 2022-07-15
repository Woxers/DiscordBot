import asyncio
from pickle import NONE
from unittest.mock import NonCallableMagicMock
import discord

from discord.ext import commands

from logger import log_error, log_info
from config import get_color, config

from database import Database

class WelcomeCog(commands.Cog):
    __invites = None

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.__invites = await self.bot.guild.invites()
        log_info("Welcome Module successfully loaded!")

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        log_info(f'Invite was created: {invite.code}')
        self.__invites = await self.bot.guild.invites()

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        log_info(f'Invite was deleted: {invite.code}')
        self.__invites = await self.bot.guild.invites()

    #####################################
    ##           MEMBER JOIN           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Ignore if not from target guild
        if (not member.guild == self.bot.guild):
            return

        # Find who invited user
        log_info(f'User joined: {member.mention}')
            # Who invited
        invites_before_join = self.__invites
        invites_after_join = await member.guild.invites()
        inviteCode = None
        inviter = None
            # Compare invites
        for invite in invites_before_join:
            sp_inv = self.find_invite_by_code(invites_after_join, invite.code)
            # Invite was deleted after use
            if (sp_inv == None):
                inviteCode = invite.code
                inviter = invite.inviter
                self.__invites = await self.bot.guild.invites()
                break
            # Invite was NOT delete after use
            elif invite.uses < sp_inv.uses:
                inviteCode = invite.code
                inviter = invite.inviter
                self.__invites = await self.bot.guild.invites()
                break

        print(f'Invite info: {inviteCode}  -  {inviter.name}')

        # Database check


    @commands.command(name='test')
    @commands.has_permissions(administrator = True)
    async def test(self, ctx, arg = None):
        dt = dict()
        dt['USER_NAME'] = 'Aptem'
        dt['USER_MENTION'] = '<@222746438814138368>'
        dt['URL'] = 'https://ictis.alex-b.me/'
        dt['COLOR'] = get_color('neutral')
        dt['TIMESTAMP'] = '2022-07-15 13:04:06'
        await self.bot.send_json_embed(ctx, 'example/key.txt', replace_dict=dt, delete_after = 10)

    # Function for finding inviter
    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv
        return None

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))