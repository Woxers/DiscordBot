from discord.ext import commands

from logger import log_error, log_info, log_debug, log_warning
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
    ##         MEMBER JOINED           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Ignore if not from target guild
        if (not member.guild == self.bot.guild):
            log_warning(f'User {member.mention} joined in unknown guild!')
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
            # Invite was NOT deleted after use
            elif invite.uses < sp_inv.uses:
                inviteCode = invite.code
                inviter = invite.inviter
                self.__invites = await self.bot.guild.invites()
                break

        log_info(f'Invite info: {inviteCode}  -  {inviter.name}')

        print(inviter.id)

        # Database check
        if (Database.ckeck_user(member.id)):
            log_debug(f'{member.mention} exist in database')
            db_user = Database.get_user_by_id(member.id)
            if (db_user['status'].lower() == 'joined'):
                log_debug('Status: JOINED')
            elif (db_user['status'].lower() == 'rejected'.lower()):
                log_debug('Status: REJECTED')
            elif (db_user['status'].lower() == 'spectator'):
                log_debug('Status: SPECTATOR')
            elif (db_user['status'].lower() == 'access'):
                log_debug('Status: ACCESS')
            elif (db_user['status'].lower() == 'verified'):
                log_debug('Status: VERIFIED')
            else:
                log_error(f'Unable to identify user status: {db_user["status"]}')
        else:
            log_debug(f'{member.mention} not exist in database')
            if (not Database.add_user(member.id, inviter.id)):
                log_error(f'Cannot add user {member.id} to database!')
                return
            log_debug('Status: JOINED')
        
        await member.kick()



    @commands.command(name='test')
    @commands.has_permissions(administrator = True)
    async def test(self, ctx, arg = None):
        dt = dict()
        dt['USER_NAME'] = 'Aptem'
        dt['USER_MENTION'] = '<@222746438814138368>'
        dt['URL'] = 'https://github.com/Woxerss'
        dt['COLOR'] = get_color('neutral')
        dt['TIMESTAMP'] = '2022-07-15 13:04:06'
        await self.bot.send_json_embed(ctx, 'example/key.txt', replace_dict=dt, delete_after = 10)

    # Find invite with code
    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv
        return None

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))