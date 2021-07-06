import discord
from discord.ext import commands
import os

class Leveling(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(Leveling(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
