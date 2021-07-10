import discord
from discord.ext import commands, tasks
import random
import json
import os
import asyncio
import cogs.users as users
import settings

TRIVIA_PATH = './data/trivia.json'
TRIVIA_PAY = settings.payouts['trivia']
TRIVIA_CHANNEL = 863164248607424523


class Trivia(commands.Cog):
    def __init__(self, client):
        self.client = client
        # self.trivia.start()

    # @commands.has_role('Robot Overlords')
    # async def triviaquestion(self, ctx):
    #     channel = self.client.get_channel(TRIVIA_CHANNEL)
    #     if ctx.channel == channel:
    #         await self.trivia()
    #     else:
    #         await ctx.send(f"Try again in {channel.mention}.")

    # @tasks.loop(hours=2)
    @commands.command(aliases=['q', 'question'])
    async def trivia(self):
        await self.client.wait_until_ready()
        ctx = self.client.get_channel(TRIVIA_CHANNEL)
        question = load_question()
        embed = discord.Embed(title='Trivia Question')

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
        timeout = 60    # Initial time to wait for response, to allow enough time to read question
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=timeout, check=check_not_bot)
                await msg.remove_reaction(reaction, user)

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
                        answers.append(answer)
                        timeout = 30  # Time to wait for response from others

                else:
                    print("Unknown reaction")

            except asyncio.TimeoutError:
                await ctx.send(
                    "Time has run out! Lets calculate some bullshit now...")

                for answer in answers:
                    print(
                        f'{answer["user"].display_name} : {answer["answer"]}')
                print('\n\n')
                await check_answers(ctx, question, answers)
                break


def load_question():
    file = open(TRIVIA_PATH, 'r', encoding='utf-8')
    questions = json.load(file)
    return random.choice(questions)


async def check_answers(ctx, question, answers):
    correct_users = []
    for answer in answers:
        if answer['answer'] == question['answer']:
            correct_users.append(answer['user'])

    correct_string = ''

    if len(correct_users) == 0:
        await ctx.send("Nobody got the answer right!")
    if len(correct_users) == 1:
        await ctx.send(f'{correct_users[0].display_name} was the only person to answer correctly and receive ₷{TRIVIA_PAY}!')
        users.give_money(correct_users[0], TRIVIA_PAY)
    if len(correct_users) == 2:
        await ctx.send(f'{correct_users[0].display_name} and {correct_users[1].display_name} got the answer correct and received ₷{TRIVIA_PAY}!')
        users.give_money(correct_users[0], TRIVIA_PAY)
        users.give_money(correct_users[1], TRIVIA_PAY)
    if len(correct_users) > 2:
        for user in correct_users:
            if user == correct_users[-1]:
                correct_string += f'and {user.display_name}'
            else:
                correct_string += f'{user.display_name}, '
            users.give_money(user, TRIVIA_PAY)
        correct_string += f' got the answer correct and received ₷{TRIVIA_PAY}!'
        await ctx.send(correct_string)


def setup(client):
    client.add_cog(Trivia(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
