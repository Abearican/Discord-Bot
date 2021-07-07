import discord
from discord.ext import commands
import os
import errno
import datetime as dt
import time


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

        log_message(message)

        if message.author == self.client.user:
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # This will apply to any server the bot is in
        print(f'{member} has joined a server!')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'{member} has left a server!')  # Ditto

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please include required arguments\nFor help use `.help [command]`.')
        else:
            print(error)


def setup(client):
    client.add_cog(Events(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')


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
