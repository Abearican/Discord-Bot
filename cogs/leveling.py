import discord
from discord.ext import commands
import os
import cogs.users as uinfo
import json
import math
import settings

# Remaining XP til next level formula (Yoinked from Mee6 github docs bere:
#                        https://github.com/Mee6/Mee6-documentation/blob/master/docs/levels_xp.md )
# 5lvl² + 50lvl + 100
# 5*(lvl**2) + 50*lvl + 100

# amount of xp to be gained from chat messages
CHAT_XP = settings.payouts['chat_xp']


class Leveling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if(uinfo.is_registered(message.author)):
                uinfo.give_xp(message.author, CHAT_XP)
                await check_level_up(message.channel, message.author)
            else:
                uinfo.register_user(message.author)

    @commands.command(aliases=['rank', 'level', 'xp'])
    async def stats(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author

        embed = discord.Embed(
            title=f'{user.display_name}\'s Stats', inline=False)

        progress = level_progress(user)

        embed.add_field(
            name='Level', value=f'{user_level(user)}', inline=True)
        embed.add_field(
            name='Rank', value=f'{user_rank(user)}', inline=True)
        embed.add_field(
            name='Total XP', value=f'{uinfo.user_xp(user)}', inline=True)

        embed.add_field(
            name='Spesos', value=f'₷{uinfo.user_money(user)}', inline=True)
        embed.add_field(
            name='Items:', value='WIP', inline=True)

        bar_size = 13
        blue_boxes = math.floor(
            progress/lvl_up_func(user_level(user)) * bar_size)
        white_boxes = bar_size - blue_boxes

        progress_bar = ''
        for x in range(blue_boxes):
            progress_bar += ':blue_square:'
        for x in range(white_boxes):
            progress_bar += ':white_large_square:'

        embed.add_field(
            name='Level Progress', value=f'{progress}/{lvl_up_func(user_level(user))}\n{progress_bar}', inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['top', 'hiscores'])
    async def leaderboard(self, ctx, query='xp'):
        if query.lower() != 'money':
            query = 'xp'

        users = uinfo.load_json()
        sorted_users = sorted(
            users, key=lambda x: x[query], reverse=True)

        embed = discord.Embed(title='Leaderboard')
        rank = 1

        for u in sorted_users:
            user = self.client.get_user(u['id'])
            if rank <= 10:
                if query == 'xp':
                    embed.add_field(
                        name=f'{rank}. {u["name"]} (Level {user_level(user)})', value=f'{u[query]} XP', inline=False)
                if query == 'money':
                    embed.add_field(
                        name=f'{rank}. {user.display_name} (Level {user_level(user)})', value=f'₷{u[query]}', inline=False)
            rank += 1
        embed.set_thumbnail(url=self.client.get_user(
            860712144537911306).avatar_url)
        await ctx.send(embed=embed)


async def check_level_up(ctx, user):
    if uinfo.user_level(user) < user_level(user):
        await ctx.send(
            f'Congratulations {user.mention}! You reached level {user_level(user)}!')
    elif uinfo.user_level(user) > user_level(user):
        await ctx.send(f'{user.mention}, you somehow have a higher level than you should. You are now level {user_level(user)}')
    else:
        return

    level_up(user, user_level(user) - uinfo.user_level(user))


def level_up(user, levels=1):
    users = uinfo.load_json()
    user = uinfo.get_user_object(user, users)
    user['level'] += levels
    uinfo.save_json(users)


def user_level(user):
    lvl = 0
    remaining_xp = uinfo.get_user_object(user)['xp']
    if remaining_xp >= 100:
        while remaining_xp >= lvl_up_func(lvl):
            remaining_xp -= lvl_up_func(lvl)
            lvl += 1
    return lvl


def user_rank(user):
    users = uinfo.load_json()
    users.sort(key=lambda x: x['xp'], reverse=True)
    user_obj = uinfo.get_user_object(user, users)

    return users.index(user_obj)+1


def xp_til_level(user):
    lvl = user_level(user)
    return lvl_up_func(lvl) - level_progress(user)


def level_progress(user):
    lvl = 0
    remaining_xp = uinfo.get_user_object(user)['xp']
    if remaining_xp > 100:
        while remaining_xp >= lvl_up_func(lvl):
            remaining_xp -= lvl_up_func(lvl)
            lvl += 1
    return remaining_xp


def lvl_up_func(lvl):
    return (5 * (lvl**2) + (50 * lvl) + 100)


def setup(client):
    client.add_cog(Leveling(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
