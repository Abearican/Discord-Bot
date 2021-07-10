import discord
import os
from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    ### BASIC PING COMMAND WITH LATENCY ###
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! in {round(self.client.latency * 1000)}ms')

    ### CLEAR X MESSAGES ###
    @commands.command()
    @commands.has_role('Robot Overlords')
    async def clear(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(f'Removed {amount} messages.')

    ### LOAD EXTENSIONS WITHIN DISCORD ###
    @commands.command(aliases=['l'])
    @commands.has_role('Robot Overlords')
    async def load(self, ctx, extension):
        await ctx.send(f'Loading `{extension}`...')
        try:
            self.client.load_extension(f'cogs.{extension}')
        except Exception as e:
            await ctx.send(f'**There was a problem loading `{extension}`.**')
            print(e)
            return
        await ctx.send(f'`{extension}` loaded successfully!')

    ### UNLOAD EXTENSIONS WITHIN DISCORD ###
    @commands.command(aliases=['ul'])
    @commands.has_role('Robot Overlords')
    async def unload(self, ctx, extension):
        await ctx.send(f'Unloading `{extension}`...')
        try:
            self.client.unload_extension(f'cogs.{extension}')
        except Exception as e:
            await ctx.send(f'**There was a problem unloading `{extension}`.**')
            print(e)
            return
        await ctx.send(f'`{extension}` unloaded successfully!')

    ### RELOAD EXTENSIONS WITHIN DISCORD ###
    @commands.command(aliases=['rl'])
    @commands.has_role('Robot Overlords')
    async def reload(self, ctx, extension):
        await ctx.send(f'Attempting to reload `{extension}`...')
        await self.unload(ctx, extension)
        await self.load(ctx, extension)
        print('\n\n\t\t\tLINE BREAKS WOO!\n\n')


def setup(client):
    client.add_cog(Admin(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')
