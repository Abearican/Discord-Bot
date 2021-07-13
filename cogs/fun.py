import discord
from discord.ext import commands
import os
import random


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    ### SIMPLE ROCK PAPER SCISSORS GAME ###
    @commands.command(aliases=['rockpaperscissors', 'rps'])
    async def roshambo(self, ctx, selection):
        bot = self.client.user.name
        botSelection = random.randrange(1, 4)  # rock, paper, scissors

        if selection.lower() == 'rock':
            await ctx.send(f'{ctx.author.name} chose [Rock]!')
            if botSelection == 1:
                await ctx.send(f'{bot} chose [Rock]!')
                await ctx.send(f'It\'s a draw!')
            if botSelection == 2:
                await ctx.send(f'{bot} chose [Paper]!')
                await ctx.send(f'{bot} wins!')
            if botSelection == 3:
                await ctx.send(f'{bot} chose [Scissors]!')
                await ctx.send(f'{ctx.author.name} wins')

        elif selection.lower() == 'paper':
            await ctx.send(f'{ctx.author.name} chose [Paper]!')
            if botSelection == 1:
                await ctx.send(f'{bot} chose [Rock]!')
                await ctx.send(f'{ctx.author.name} wins')
            if botSelection == 2:
                await ctx.send(f'{bot} chose [Paper]!')
                await ctx.send(f'It\'s a draw!')
            if botSelection == 3:
                await ctx.send(f'{bot} chose [Scissors]!')
                await ctx.send(f'{bot} wins!')

        elif selection.lower() == 'scissors':
            await ctx.send(f'{ctx.author.name} chose [Scissors]!')
            if botSelection == 1:
                await ctx.send(f'{bot} chose [Rock]!')
                await ctx.send(f'{bot} wins!')
            if botSelection == 2:
                await ctx.send(f'{bot} chose [Paper]!')
                await ctx.send(f'{ctx.author.name} wins')
            if botSelection == 3:
                await ctx.send(f'{bot} chose [Scissors]!')
                await ctx.send(f'It\'s a draw!')

        else:
            await ctx.send('Please make a valid selection (rock/paper/scissors)')

    ### 8BALL: ASK QUESTION; RECIEVE ANSWER! ###
    @commands.command(aliases=['8ball', 'ask'])
    async def magicball(self, ctx, *, question):
        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
                     "Don’t count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.", "My sources say no.",
                     "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.",
                     "Yes.", "Yes – definitely.", "You may rely on it."]
        await ctx.send(f'Question: {question}\n{random.choice(responses)}')

    # Rolls dice. Type and amount optional. Defaults to 1 D6.
    @commands.command(aliases=['dice'])
    async def roll(self, ctx, die_type='d6', amount=1):
        try:
            size = int(die_type.lower().lstrip('d'))
        except:
            await ctx.send('Please enter your die type formatted such as `d20` or `D8`.')
            return
        if (size < 0):
            await ctx.send('You expect me to roll a die with a negative amount of sides? Fuck off.')
            return
        if (size == 0):
            await ctx.send('You asked me to roll a dice with no sides? Fuck off innit.')
            return
        else:
            rolls = ''

            for i in range(amount):
                rolls += f'[{random.randint(1, size)}] '

            await ctx.send(f'I rolled {amount} D{size}(s) for you!\n{rolls}')

    ### Coinflip. Simple. ###
    @commands.command()
    async def coinflip(self, ctx):
        if random.randint(0, 1):
            await ctx.send(file=discord.File('./resources/heads.png'))
        else:
            await ctx.send(file=discord.File('./resources/tails.png'))

    ### Draw random card (non duplicate!) ###
    @commands.command(aliases=['drawcard'])
    async def draw(self, ctx, amount=1):
        faces = ['Ace', '2', '3', '4', '5', '6', '7',
                 '8', '9', '10', 'Jack', 'Queen', 'King']
        suits = ['Spades', 'Hearts', 'Clubs', 'Diamonds']

        if not isinstance(amount, int):
            await ctx.send('Amount must be a number 52 or less or omitted for a single card.\n\
                Type `!help drawcard` for help.')
        elif amount > 52:
            await ctx.send('Theres only 52 cards in a deck you turd.')
        elif amount < 1:
            await ctx.send('Is this some sort of joke?')
        elif amount == 1:
            await ctx.send(f'Your card is the [{random.choice(faces)} of {random.choice(suits)}]!')
        else:
            message = f'Your {amount} cards:\n'
            cards = []
            for i in range(amount):
                card = (random.choice(faces), random.choice(suits))
                while card in cards:
                    card = (random.choice(faces), random.choice(suits))
                cards.append(card)

            for card in cards:
                message += f'[{card[0]} of {card[1]}]\n'

            await ctx.send(message)


def setup(client):
    client.add_cog(Fun(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
