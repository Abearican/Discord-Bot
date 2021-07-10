import discord
from discord.ext import commands
import json
import os
import math


class User_Info(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command(aliases=['reg'])
    async def register(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author

        if is_registered(user):
            await ctx.send(f'{user.name} is already registered!')
        else:
            register_user(user)
            await ctx.send("New user registered!")

    @commands.command()
    async def pay(self, ctx, amount: int, recipient: discord.Member):
        payee = ctx.author

        if not is_registered(payee):
            register_user(payee)
        if not is_registered(recipient):
            register_user(recipient)

        if(user_money(payee) < amount):
            await ctx.send(f'Broke bitch! :joy::joy::joy: You don\'t have enough Shrimp :joy: (Balance: `₷{user_money(payee)}`)')
        elif(amount < 0):
            fine_amount = math.ceil(user_money(payee)/5)
            take_money(payee, fine_amount)
            await ctx.send(f'Stop thief!\n`You were caught and had to pay a fine of ₷{fine_amount}`')
        else:
            take_money(payee, amount)
            give_money(recipient, amount)
            await ctx.send(f'₷{amount} payed to {recipient.display_name}!')


def user_level(user):
    return get_user_object(user)['level']


def user_xp(user: discord.Member):
    return get_user_object(user)['xp']


def user_money(user: discord.Member):
    return get_user_object(user)['money']


def give_xp(user, amount):
    users = load_json()
    user_obj = get_user_object(user, users)
    user_obj['xp'] += amount
    user_obj['name'] = user.display_name
    save_json(users)


def give_money(user: discord.Member, amount):
    users = load_json()
    user_obj = get_user_object(user, users)
    user_obj['money'] += amount
    save_json(users)


def take_money(user: discord.Member, amount):
    users = load_json()
    user_obj = get_user_object(user, users)
    user_obj['money'] -= amount
    save_json(users)


def verify_display_name(user: discord.Member):
    user_obj = get_user_object(user)
    if not user_obj['name'] == user.display_name:
        users = load_json(user)
        user_obj = get_user_object(user, users)
        user_obj['name'] = user.display_name
        save_json(users)


def register_user(user):
    users = load_json()
    new_user = {
        'id': user.id,
        'name': user.display_name,
        'username': user.name,
        'level': 1,
        'xp': 100,
        'money': 69
    }
    users.append(new_user)

    save_json(users)


def is_registered(user: discord.Member):
    users = load_json()
    for user_obj in users:
        if user_obj['id'] == user.id:
            return True
    return False


def get_user_object(user: discord.Member, users=None):
    if not users:
        users = load_json()
    for u in users:
        if user.id == u['id']:
            return u

    # Register user if the function could not find a matching user object, then try again
    register_user(user)
    get_user_object(user)


def save_json(new_data):
    with open('./data/userdata.json', 'w', encoding='utf-8') as json_file:
        json.dump(new_data, json_file, indent=2)


def load_json():
    with open('./data/userdata.json', 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def setup(client):
    client.add_cog(User_Info(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
