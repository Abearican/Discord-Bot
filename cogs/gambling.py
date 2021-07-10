import discord
from discord.ext import commands
import os
import cogs.users as users
import asyncio
import random as rand


class Gambling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['711'])
    async def seveneleven(self, ctx, bet: int):

        if bet > users.user_money(ctx.author):
            await ctx.send("You are a broke bitch lol try betting a lower amount.")
            return

        msg = await ctx.send(f'You wish to bet ₷{bet}. Confirm?')
        emojis = ['👍', '👎']

        for emoji in emojis:
            await msg.add_reaction(emoji)

        def check(reaction, user):
            return reaction.emoji in emojis and not user.bot

        played = False

        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=20, check=check)
                await msg.remove_reaction(reaction, user)

                if user == ctx.author:
                    if reaction.emoji == '👍':
                        if played:
                            bet += bet

                        await ctx.send('Very well. I will role some dice...')

                        dice = [rand.randint(1, 6), rand.randint(1, 6)]
                        await ctx.send(f'[{dice[0]}] and [{dice[1]}]\nThat totals to {dice[0]+dice[1]}.')

                        if dice[0]+dice[1] == 7 or dice[0]+dice[1] == 11:
                            await ctx.send(f'Tough luck, {user.display_name}. I\'ll be takin\' ya money, mate!')
                            await ctx.send(f'`You lost ₷{bet}.`')
                            users.take_money(user, bet)
                            break
                        else:
                            exclames = ['Good stuff! ',
                                        'Sheeeeeesh! ',
                                        'It\' your lucky day! ',
                                        'Are you trying to take all my money? ',
                                        'Alright! ']
                            retry = await ctx.send(f'{rand.choice(exclames)} What do you say? Double or nothing?\nCurrent bet: ₷{bet}\tCash out: ₷{bet+bet}')
                            for emoji in emojis:
                                await retry.add_reaction(emoji)

                            played = True
                    else:
                        if played:
                            await ctx.send('As you wish.')
                            await ctx.send(f'`Cashing out ₷{bet+bet}`')
                            users.give_money(user, bet)
                        else:
                            await ctx.send('Well run the command again and bet the correct amount this time. Sheesh.')
                        break
                else:
                    await ctx.send(f'Fuck off {user.mention}! Wait your god damn turn!')

            except asyncio.TimeoutError:
                await ctx.send(
                    "If you are going to play the game, play the game. Fee not refunded for wasting my time.")
                users.take_money(ctx.author, bet)
                break


def setup(client):
    client.add_cog(Gambling(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
