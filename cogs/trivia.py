import discord
from discord.ext import commands
import random
import json
import os
import asyncio
import cogs.users as users
import settings

TRIVIA_PATH = settings.paths['trivia']
TRIVIA_PAY = settings.payouts['trivia_money']
TRIVIA_CHANNEL = settings.channels['trivia']
TRIVIA_ROUNDS = settings.other['trivia_rounds']


class Trivia(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.trivia_channel = client.get_channel(TRIVIA_CHANNEL)

    # @commands.has_role('Robot Overlords')
    # async def triviaquestion(self, ctx):
    #     channel = self.client.get_channel(TRIVIA_CHANNEL)
    #     if ctx.channel == channel:
    #         await self.trivia()
    #     else:
    #         await ctx.send(f"Try again in {channel.mention}.")

    # @tasks.loop(hours=2)
    @commands.command(aliases=['q', 'question'])
    @commands.cooldown(1, 43200, commands.BucketType.guild)
    async def trivia(self, ctx):
        if not ctx.channel == self.trivia_channel:
            await ctx.send(f"{ctx.author.mention}, try again in {self.trivia_channel.mention}!")
            self.trivia.reset_cooldown(ctx)
            return

        await self.play_trivia(ctx)

    @trivia.error
    async def trivia_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time_left = (error.retry_after)/60/60
            await ctx.send(f'This command is on cooldown, you can use it in {round(time_left, 1)} hours!')
        else:
            print(error)

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
            timeout = 30    # Initial time to wait for response, to allow enough time to read question and think
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
                                timeout = 15  # Time to wait for response from others

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

        embed = discord.Embed(title="Results")

        hiscores = sorted(
            scores, key=lambda x: x['score'], reverse=True)

        for index, score in enumerate(hiscores):
            if score == hiscores[0]:
                winnings = 50
            elif score == hiscores[1]:
                if score['score'] == hiscores[0]['score']:
                    winnings = 50
                else:
                    winnings = 35
            elif score == hiscores[2]:
                if score['score'] == hiscores[1]['score']:
                    winnings = 35
                elif score['score'] == hiscores[0]['score']:
                    winnings = 50
                else:
                    winnings = 20
            else:
                winnings = 0

            embed.add_field(
                name=f"{index + 1}. {score['player'].display_name}", value=f'{score["score"]} points\nWinnings: ₷{winnings}')
            users.give_money(score['player'], winnings)

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

    # correct_users = []
    # for answer in answers:
    #     if answer['answer'] == question['answer']:
    #         correct_users.append(answer['user'])

    # correct_string = ''

    # if len(correct_users) == 0:
    #     await ctx.send("Nobody got the answer right!")
    # if len(correct_users) == 1:
    #     await ctx.send(f'{correct_users[0].display_name} was the only person to answer correctly and receive ₷{TRIVIA_PAY}!')
    #     users.give_money(correct_users[0], TRIVIA_PAY)
    # if len(correct_users) == 2:
    #     await ctx.send(f'{correct_users[0].display_name} and {correct_users[1].display_name} got the answer correct and received ₷{TRIVIA_PAY}!')
    #     users.give_money(correct_users[0], TRIVIA_PAY)
    #     users.give_money(correct_users[1], TRIVIA_PAY)
    # if len(correct_users) > 2:
    #     for user in correct_users:
    #         if user == correct_users[-1]:
    #             correct_string += f'and {user.display_name}'
    #         else:
    #             correct_string += f'{user.display_name}, '
    #         users.give_money(user, TRIVIA_PAY)
    #     correct_string += f' got the answer correct and received ₷{TRIVIA_PAY}!'
    #     await ctx.send(correct_string)
