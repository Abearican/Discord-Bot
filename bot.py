import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        try:
            client.load_extension(f'cogs.{filename[:-3]}')
        except Exception as e:
            print(e)
            break

client.run(TOKEN)
