import discord
from discord.ext import commands
import random
import json
import os
import asyncio
import cogs.users as users
import settings
import math

# All variables can be changed from settings.py in bot's root directory
TRIVIA_PATH = settings.paths['trivia']
TRIVIA_CHANNEL_ID = settings.channels['trivia']
TRIVIA_PAY = settings.trivia['trivia_pay']
PLAYER_REQUIREMENT = settings.trivia['player_requirement']
TRIVIA_ROUNDS = settings.trivia['trivia_rounds']
ROUND_TIME = settings.trivia['round_time']


class Trivia(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['q', 'question'])
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def trivia(self, ctx):
        # Limits command to trivia channel only
        trivia_channel = self.client.get_channel(TRIVIA_CHANNEL_ID)
        if not ctx.channel == trivia_channel:
            await ctx.send(f"Try again in {trivia_channel.mention}")
            self.trivia.reset_cooldown(ctx)
            return

        # Obtain a list of players who have signed up to play
        players = await self.trivia_signup(ctx)

        # Makes sure enough players have signed up
        if len(players) < PLAYER_REQUIREMENT:
            await ctx.send("Not enough players signed up! Game not started.")
            self.trivia.reset_cooldown(ctx)
            return

        # Creates an empty scoreboard
        scores = []
        for player in players:
            scores.append({
                "player": player,
                "score": 0
            })

        # Loops for the desired amount of rounds to play
        for x in range(TRIVIA_ROUNDS):
            # Loads the question object and displays question
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

            # Adds emoji reactions to represent multiple choice selections
            emojis = ['🇦', '🇧', '🇨', '🇩']
            for emoji in emojis:
                await msg.add_reaction(emoji=emoji)

            # Check function for wait_for() command
            def user_check(reaction, user):
                # Checks if user is a bot reacting to its own message
                if user.bot:
                    return False

                # Checks if one of the selection emojis are used, otherwise remove it, return NOPE
                if not reaction.emoji in emojis:
                    return False

                # Passes all checks, returns true
                return True

            # Initial variables to be modified through loop
            timeout = ROUND_TIME
            correct_user_string = '*Correct*:'
            responses = []
            letter_selection = ['A', 'B', 'C', 'D']

            # This will break once all responses are gathered or time runs out.
            while True:
                try:
                    # Waiting for a reaction to question embed, then removes it
                    reaction, user = await self.client.wait_for("reaction_add", timeout=timeout, check=user_check)
                    await msg.remove_reaction(reaction, user)

                    # Checks if reaction user is one of the players.  Continue while loop if so.
                    if not user in players:
                        ctx.send(
                            f'You will have to sign up for the next game, {user.mention}!')
                        continue

                    # Checks if player already submitted a response. Continue while loop if so.
                    answered = False
                    for a in responses:
                        if user == a['user']:
                            await ctx.send(f"Sorry, {user.mention}! You cannot change your answer after submitting.")
                            answered = True
                            break
                    if answered:
                        continue

                    # Create a response object with the user and letter answer as values
                    response = {
                        "user": user,
                        "answer": letter_selection[emojis.index(reaction.emoji)]
                    }

                    # If correct answer...
                    if check_answer(question, response['answer']):
                        # Contatonate username onto correct_user_string
                        correct_user_string += f'\n{user.display_name}'

                        # Award player a point on scoreboard
                        for score in scores:
                            if score['player'] == user:
                                score['score'] += 1

                    # Append the answer with the rest of the answers
                    responses.append(response)

                    # Time to wait for response from others
                    timeout = math.floor(ROUND_TIME/2)

                    # Checks if all players have responded
                    if len(players) == len(responses):
                        # Displays correct users and practically ends the timeout for wait_for command
                        await ctx.send('All players Have answered.')
                        if correct_user_string == '*Correct*:':
                            correct_user_string += '\nNone!'
                        await ctx.send(correct_user_string)
                        timeout = 3

                # What happens when nobody reacts before timeout
                except asyncio.TimeoutError:
                    # What to send if it is not last round
                    if x < TRIVIA_ROUNDS - 1:
                        await ctx.send("On to the next question!")
                    # What to send if it is last round
                    else:
                        await ctx.send("Pencils down! That was the last question. Totalling answers now...")

                    # Displays all responses to console
                    for response in responses:
                        print(
                            f'{response["user"].display_name} : {response["answer"]}')
                    print()

                    # Breaks 'while True' loop
                    break

        await score_game(ctx, scores)
        self.trivia.reset_cooldown(ctx)

    async def trivia_signup(self, ctx):

        # Setting up our fancy signup embed
        embed = discord.Embed(title="Trivia Signup in progress!")
        embed.set_thumbnail(
            url='https://www.nicepng.com/png/full/232-2328543_trivia-icon.png')
        embed.add_field(name='Players:',
                        value="(Press the ballot box reaction to join.)")
        signup = await ctx.send(embed=embed)

        await signup.add_reaction(emoji='🗳️')

        # Players will get added here once they react to join the game
        players_signed_up = []

        # bot check
        def check_not_bot(reaction, user):
            return not user.bot

        # Will break once reaction response times out
        # This is just the silly way of getting responses
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=10, check=check_not_bot)
                await signup.remove_reaction(reaction, user)

                if reaction.emoji == '🗳️':
                    # Checks if user has signed up
                    if user in players_signed_up:
                        await ctx.send(f'{user.mention}, you have already signed up!')

                    else:
                        # Adds user to trivia signup list
                        players_signed_up.append(user)
                        # ... and adds a field for them
                        embed.add_field(
                            name=f'{user.display_name}', value=f'Trivia Score: {users.trivia_score(user)}', inline=False)
                        await signup.edit(embed=embed)
                else:
                    print("Unknown reaction")

            # Reaction response time out
            except asyncio.TimeoutError:
                await ctx.send("Trivia signup is closed!")
                break

        return players_signed_up


# This function calculates and awards winnings and displays a leaderboard for the game
async def score_game(ctx, scores):

    # Sorts scores by game score
    hiscores = sorted(
        scores, key=lambda x: x['score'], reverse=True)

    # Creating the title for our leaderboard
    embed = discord.Embed(title="Results")

    # Grabbing an index so we can calculate placement throughout hiscores
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
        player_score = score['score']

        # As long as you place within the rankings that receive pay, you will get some winning
        # This allows us, in settings.py, to specify winnings for any amount of rankings
        if placement < len(TRIVIA_PAY):
            winnings = TRIVIA_PAY[placement-1]
        else:
            winnings = 0

        # Give user their winnings and trivia points
        users.give_money(player, winnings)
        users.give_trivia_points(player, player_score)

        # Add player, score, and winnings to leaderboard
        embed.add_field(
            name=f"{placement}. {player.display_name}", value=f'Score: {player_score}\nWinnings: ₷{winnings}', inline=False)

    # Set thumbnail and display leaderboard
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
