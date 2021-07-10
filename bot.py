import os
import discord
import json
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)

json_file = open('./data/userdata.json', 'r', encoding='utf-8')
users = json.load(json_file)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename[0] != '_':
        try:
            client.load_extension(f'cogs.{filename[:-3]}')
        except Exception as e:
            print(e)

client.run(TOKEN)
