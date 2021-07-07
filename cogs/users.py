import discord
from discord.ext import commands
import json
import os
import math

from pymongo.periodic_executor import _register_executor


class User_Info(commands.Cog):
    def __init__(self, ctx):
        self.ctx = ctx

    @commands.command()
    async def pay(self, ctx, recipient: discord.Member, amount: int):
        users = self.load_json()
        payee = None
        rec = None

        for user in users['users']:
            if ctx.author.id == user['id']:
                payee = user
            if recipient.id == user['id']:
                rec = user

        if not payee:
            await ctx.send(f'You are not registered yet! Registering user now...')
            self.register_user(ctx.author)
        if not rec:
            await ctx.send(f'{recipient.display_name} is not registered yet! Registering user now...')
            self.register_user(recipient)
        if not payee or not rec:
            return

        if(payee['money'] < amount):
            await ctx.send(f'Broke bitch! :joy::joy::joy: You don\'t have enough Shrimp :joy: (Balance: `₷{payee["money"]}`)')
        elif(amount < 0):
            fine_amount = math.ceil(payee['money']/5)
            payee['money'] -= fine_amount
            await ctx.send(f'Stop thief!\n`You were caught and had to pay a fine of ₷{fine_amount}`')
            self.save_json(users)
        else:
            payee['money'] -= amount
            rec['money'] += amount
            await ctx.send(f'₷{amount} payed to {recipient.display_name}!')
            self.save_json(users)

    @commands.command(aliases=['bal'])
    async def balance(self, ctx, user: discord.Member = None):
        users = self.load_json()
        if not user:
            user = ctx.author
        for u in users['users']:
            if u['id'] == user.id:
                await ctx.send(f'The balance for {user.mention} is `₷{u["money"]}`')
                return
        self.register_user(user)

    @commands.command(aliases=['reg'])
    async def register(self, ctx, user: discord.Member = None):
        users = self.load_json()
        if not user:
            user = ctx.author
        for userid in users['users']:
            if userid['id'] == user.id:
                await ctx.send(f'{user.name} is already registered!')
                return
        self.register_user(user)
        await ctx.send("New user registered! *(Hopefully)*")

    def register_user(self, user):
        users = self.load_json()
        new_user = {
            'id': user.id,
            'name': user.name,
            'xp': 0,
            'money': 69
        }
        users['users'].append(new_user)

        self.save_json(users)

    def save_json(self, new_data):
        with open('./data/userdata.json', 'w', encoding='utf-8') as json_file:
            json.dump(new_data, json_file, indent=2)

    def load_json(self):
        with open('./data/userdata.json', 'r', encoding='utf-8') as json_file:
            return json.load(json_file)


def setup(client):
    client.add_cog(User_Info(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')

# "users": [
    # {
    #     "id": "4206942069",
    #     "name": "Test User",
    #     "xp": 420,
    #     "money": 69
