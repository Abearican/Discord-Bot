import discord
from discord.ext import commands
import random
import json
import os
import asyncio
import cogs.users as users
import settings
import math

TRIVIA_PATH = settings.paths['trivia']
TRIVIA_CHANNEL_ID = settings.channels['trivia']
TRIVIA_PAY = settings.trivia['trivia_pay']
TRIVIA_ROUNDS = settings.trivia['trivia_rounds']
ROUND_TIME = settings.trivia['round_time']


class Trivia(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def trivia_night(self, ctx):
        await self.trivia(ctx)

    # @tasks.loop(hours=2)
    @commands.command(aliases=['q', 'question'])
    @commands.cooldown(1, 43200, commands.BucketType.guild)
    async def trivia(self, ctx):
        trivia_channel = self.client.get_channel(TRIVIA_CHANNEL_ID)
        if not ctx.channel == trivia_channel:
            await ctx.send(f"{ctx.author.mention}, try again in {trivia_channel.mention}!")
            self.trivia.reset_cooldown(ctx)
            return

        await self.play_trivia(ctx)

    async def trivia_signup(self, ctx):
        def check_not_bot(reaction, user):
            return not user.bot

        embed = discord.Embed(title="Trivia Signup in progress!")
        embed.set_thumbnail(
            url='https://www.nicepng.com/png/full/232-2328543_trivia-icon.png')
        embed.add_field(name='Players:',
                        value="(Press the ballot box reaction to join.)")
        signup = await ctx.send(embed=embed)
        await signup.add_reaction(emoji='🗳️')
        active_players = []

        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check_not_bot)
                await signup.remove_reaction(reaction, user)

                if reaction.emoji == '🗳️':
                    if user in active_players:
                        await ctx.send(f'{user.mention}, you have already signed up!')
                    else:
                        active_players.append(user)
                        embed.add_field(
                            name=f'{user.display_name}', value=f'Trivia Score: {users.trivia_score(user)}', inline=False)
                        await signup.edit(embed=embed)
                else:
                    print("Unknown reaction")

            except asyncio.TimeoutError:
                await ctx.send("Trivia signup is closed!")
                break

        return active_players

    async def play_trivia(self, ctx):
        players = await self.trivia_signup(ctx)
        if len(players) < 3:
            await ctx.send("Not enough players signed up! Game not started.")
            self.trivia.reset_cooldown(ctx)
            return

        scores = []
        for player in players:
            scores.append({
                "player": player,
                "score": 0
            })

        for x in range(TRIVIA_ROUNDS):
            question = load_question()
            embed = discord.Embed(title=f'Trivia Question {x+1}')

            embed.add_field(name='Question:',
                            value=question['question'], inline=False)
            embed.add_field(name='A:', value=question['A'], inline=False)
            embed.add_field(name='B:', value=question['B'], inline=False)
            embed.add_field(name='C:', value=question['C'], inline=False)
            embed.add_field(name='D:', value=question['D'], inline=False)
            embed.set_thumbnail(
                url='https://www.nicepng.com/png/full/232-2328543_trivia-icon.png')

            msg = await ctx.send(embed=embed)

            emojis = ['🇦', '🇧', '🇨', '🇩']

            for emoji in emojis:
                await msg.add_reaction(emoji=emoji)

            def check_not_bot(reaction, user):
                return not user.bot

            answers = []
            # Initial time to wait for response, to allow enough time to read question and think
            timeout = ROUND_TIME
            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=timeout, check=check_not_bot)
                    await msg.remove_reaction(reaction, user)

                    if user in players:
                        if reaction.emoji in emojis:
                            letter_answers = ['A', 'B', 'C', 'D']
                            answer = {
                                "user": user,
                                "answer": letter_answers[emojis.index(reaction.emoji)]
                            }
                            answered = False
                            for a in answers:
                                if answer['user'] == a['user']:
                                    await ctx.send(f"Sorry, {a['user'].mention}! You cannot change your answer after submitting.")
                                    answered = True
                                    break

                            if not answered:
                                if check_answer(question, answer['answer']):
                                    users.give_trivia_points(user, 1)
                                    for score in scores:
                                        if score['player'] == user:
                                            score['score'] += 1

                                answers.append(answer)
                                # Time to wait for response from others
                                timeout = math.floor(ROUND_TIME/2)

                        else:
                            print("Unknown reaction")
                    else:
                        await ctx.send(f'{user.mention}, you did not sign up for this round of trivia!')

                except asyncio.TimeoutError:
                    if x < TRIVIA_ROUNDS - 1:
                        await ctx.send(
                            "Time has run out! On to the next question!")
                    else:
                        await ctx.send("Time has run out! That was the last question. Totalling answers now...")

                    for answer in answers:
                        print(
                            f'{answer["user"].display_name} : {answer["answer"]}')
                    print()
                    break

        hiscores = sorted(
            scores, key=lambda x: x['score'], reverse=True)
        await score_game(ctx, hiscores)


async def score_game(ctx, hiscores):
    embed = discord.Embed(title="Results")
    for index, score in enumerate(hiscores):
        # Setting initial value according to its placement in the list
        score['placement'] = index + 1

        # If the score is the same as the previous one, the placements will be the same
        if not index == 0:
            prev = hiscores[index-1]
            if score['score'] == prev['score']:
                score['placement'] = prev['placement']

        # Dish out winnings based on placement
        placement = score['placement']
        player = score['player']

        if placement == 1:
            winnings = TRIVIA_PAY[0]
        elif placement == 2:
            winnings = TRIVIA_PAY[1]
        elif placement == 3:
            winnings = TRIVIA_PAY[2]
        else:
            winnings = 0

        users.give_money(player, winnings)

        embed.add_field(
            name=f"{placement}. {player.display_name}", value=f'Score: {score["score"]}\nWinnings: ₷{winnings}')

    embed.set_thumbnail(
        url='https://www.nicepng.com/png/full/232-2328543_trivia-icon.png')
    await ctx.send(embed=embed)


def load_question():
    file = open(TRIVIA_PATH, 'r', encoding='utf-8')
    questions = json.load(file)
    return random.choice(questions)


def check_answer(question, answer):
    return question["answer"] == answer


def setup(client):
    client.add_cog(Trivia(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
