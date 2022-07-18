import asyncio
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
        # Ignore if not from target guild
        if (not invite.guild == self.bot.guild):
            log_warning(f'Invite {invite.code} created in unknown guild!')
            return
        log_info(f'Invite was created: {invite.code}')
        self.__invites = await self.bot.guild.invites()

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        # Ignore if not from target guild
        if (not invite.guild == self.bot.guild):
            log_warning(f'Invite {invite.code} deleted in unknown guild!')
            return
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

        log_info(f'User joined: {member.mention}')

        # Find who invited user
        invites_before_join = self.__invites
        invites_after_join = await member.guild.invites()
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

        # Database check
        if (Database.ckeck_user(member.id)):
            log_debug(f'{member.mention} exist in database')
            db_user = Database.get_user_by_id(member.id)
            Database.set_active(member.id, 1)
            # Newbie joined
            if (db_user['status'].lower() == 'joined'):
                # Add role Joined
                role = self.bot.get_role_by_id(config['roles']['candidate'])
                await member.add_roles(role, reason='Auto-Role')
                log_debug(f'Added role {role.name}')
                # Send messages
                await self.bot.send_json_embed(member, 'welcome/member_joined_newbie.txt')
                dt = {'INVITE_CODE': inviteCode, 'MEMBER_ID': member.id, 'MEMBER_MENTION': member.mention}
                await self.bot.send_json_embed(inviter, 'welcome/confirm_inviter.txt', replace_dict=dt)
            # Rejected joined
            elif (db_user['status'].lower() == 'rejected'.lower()):
                # Add role Rejected
                role = self.bot.get_role_by_id(config['roles']['rejected'])
                await member.add_roles(role, reason='Auto-Role')
                log_debug(f'Added role {role.name}')
                # Send messages
                await self.bot.send_json_embed(member, 'welcome/member_joined_rejected.txt')
            # Spectator joined
            elif (db_user['status'].lower() == 'spectator'):
                # Add role Spectator
                role = self.bot.get_role_by_id(config['roles']['spectator'])
                await member.add_roles(role, reason='Auto-Role')
                log_debug(f'Added role {role.name}')
                # Send messages
                await self.bot.send_json_embed(member, 'welcome/member_joined_spectator.txt')
            # Access joined
            elif (db_user['status'].lower() == 'access'):
                Database.set_status_by_user_id(member.id, 'verified')
                # Add role Verified
                role = self.bot.get_role_by_id(config['roles']['verified'])
                await member.add_roles(role, reason='Auto-Role')
                log_debug(f'Added role {role.name}')
                # Send messages
                await self.bot.send_json_embed(member, 'welcome/member_joined_access.txt')
                await self.bot.send_json_embed(member, 'welcome/access_denied.txt')
            # Verified joined
            elif (db_user['status'].lower() == 'verified'):
                # Add role Verified
                role = self.bot.get_role_by_id(config['roles']['verified'])
                await member.add_roles(role, reason='Auto-Role')
                log_debug(f'Added role {role.name}')
                # Send messages
                await self.bot.send_json_embed(member, 'welcome/member_joined_verified.txt')
            else:
                log_error(f'Unable to identify user status: {db_user["status"]}')
        else:
            # Add to database
            log_debug(f'{member.mention} not exist in database')
            if (not Database.add_user(member.id, inviter.id)):
                log_error(f'Cannot add user {member.id} to database!')
            # Add role Candidate
            role = self.bot.get_role_by_id(config['roles']['candidate'])
            await member.add_roles(role, reason='Auto-Role')
            log_debug(f'Added role {role.name}')
            # Send messages
            await self.bot.send_json_embed(member, 'welcome/member_joined_newbie.txt')
            dt = {'INVITE_CODE': inviteCode, 'MEMBER_ID': member.id, 'MEMBER_MENTION': member.mention}
            await self.bot.send_json_embed(inviter, 'welcome/confirm_inviter.txt', replace_dict=dt)
        
        try:
            # User Joined log-channel message!
            dt = dict()
            dt['INVITER_MENTION'] = inviter.mention
            dt['INVITE_CODE'] = inviteCode
            dt['INVITED_PLAYERS_COUNT'] = Database.get_invited_players_count_by_id(inviter.id)
            dt['INVITED_COUNT'] = Database.get_invited_count_by_id(inviter.id)
            dt['STATUS'] = db_user['status'].upper()
            dt['MEMBER_MENTION'] = member.mention
            dt['MEMBER_NAME'] = member.name
            dt['MEMBER_DISCRIMINATOR'] = member.discriminator
            dt['CREATED'] = member.created_at.strftime('%Y-%m-%d')
            dt['TOTAL'] = self.bot.guild.member_count
            dt['COLOR'] = role.color.value
            await self.bot.send_json_embed(self.bot.get_channel_by_id(config['channels']['join_logs']['id']), 'welcome/log_joined.txt', replace_dict=dt)
        except Exception as e:
            log_error(e)

        await asyncio.sleep(5)
        await member.kick()

    #####################################
    ##           MEMBER LEFT           ##
    #####################################
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Ignore if not from target guild
        if (not member.guild == self.bot.guild):
            log_warning(f'User {member.mention} joined in unknown guild!')
            return
        
        log_info(f'User left: {member.mention}')
        Database.set_active(member.id, 0)

        # Database check
        if (Database.ckeck_user(member.id)):
            log_debug(f'{member.mention} exist in database')
            db_user = Database.get_user_by_id(member.id)
            # Newbie left
            if (db_user['status'].lower() == 'joined'):
                pass
            # Rejected left
            elif (db_user['status'].lower() == 'rejected'.lower()):
                pass
            # Spectator left
            elif (db_user['status'].lower() == 'spectator'):
                pass
            # Access left
            elif (db_user['status'].lower() == 'access'):
                pass
                # TODO: Revoke access to mc server!
            # Verified left
            elif (db_user['status'].lower() == 'verified'):
                pass
            else:
                log_error(f'Unable to identify user status: {db_user["status"]}')
        else:
            log_debug(f'{member.mention} not exist in database')

        try:
            # User Joined log-channel message!
            inviter = self.bot.get_member_by_id(db_user['inviter_id'])
            dt = dict()
            dt['INVITER_MENTION'] = inviter.mention
            dt['INVITE_CODE'] = 'None'
            dt['INVITED_PLAYERS_COUNT'] = Database.get_invited_players_count_by_id(inviter.id)
            dt['INVITED_COUNT'] = Database.get_invited_count_by_id(inviter.id)
            dt['STATUS'] = db_user['status'].upper()
            dt['MEMBER_MENTION'] = member.mention
            dt['MEMBER_NAME'] = member.name
            dt['MEMBER_DISCRIMINATOR'] = member.discriminator
            dt['CREATED'] = member.created_at.strftime('%Y-%m-%d')
            dt['TOTAL'] = self.bot.guild.member_count
            await self.bot.send_json_embed(self.bot.get_channel_by_id(config['channels']['join_logs']['id']), 'welcome/log_left.txt', replace_dict=dt)
        except Exception as e:
            log_error(e)
        
            


    @commands.command(name='test')
    @commands.has_permissions(administrator = True)
    async def test(self, ctx, arg = None):
        dt = dict()
        dt['USER_NAME'] = 'Aptem'
        dt['USER_MENTION'] = '<@222746438814138368>'
        dt['URL'] = 'https://github.com/Woxerss'
        dt['COLOR'] = get_color('neutral')
        #dt['TIMESTAMP'] = '2022-07-15 13:04:06'
        await self.bot.send_json_embed(ctx, 'example/key.txt', replace_dict=dt, delete_after = 10)

    # Find invite with code
    def find_invite_by_code(self, invite_list, code):
        for inv in invite_list:
            if inv.code == code:
                return inv
        return None

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))