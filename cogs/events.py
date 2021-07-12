import discord
from discord.ext import commands
import os
import errno
import datetime as dt
import time
import sys
import traceback

BOT_CHANNELS = [803372255777914911, 803375064816287814, 803380541230940161]


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            if guild.name == os.getenv('GUILD'):
                break

        print(
            f'{self.client.user.name} has connected to '
            f'{guild.name} (id: {guild.id})'
        )

        await self.client.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="you."))

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.client.user \
                or message.channel.id in BOT_CHANNELS:
            return

        log_message(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please include required arguments\nFor help use `.help [command]`.')
        else:
            print('Ignoring exception in command {}:'.format(
                ctx.command), file=sys.stderr)
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr)

# Logs all messages to the logs file in bot directory


def log_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content).replace('\n', '\n\t\t ')
    if(message.attachments):
        user_message = '<Attachment> ' + user_message
    channel = str(message.channel.name)
    today = dt.datetime.today()
    current_time = time.strftime("%H:%M:%S", time.localtime())

    log_file = f'logs/{today.strftime("%Y-%m")}/{dt.date.today()}.txt'

    if not os.path.exists(os.path.dirname(log_file)):
        try:
            os.makedirs(os.path.dirname(log_file))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise  # Idk what this whole except part means. just copied from SO

    chat_log = open(log_file, 'a', encoding='utf-8')

    chat_log.write(f'{current_time} [#{channel}] {username}: {user_message}\n')
    chat_log.close()


def setup(client):
    client.add_cog(Events(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
