import discord
from discord.ext import commands
import os
import random as rng

MEMORY_PATH = './resources/memories/'


class Memories(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def memory(self, ctx, selection=None):
        memories = []

        if not selection:
            for filename in os.listdir(MEMORY_PATH):
                memories.append(f'{MEMORY_PATH}{filename}')
            await ctx.send(file=discord.File(rng.choice(memories)))
        else:
            await ctx.send(f'{MEMORY_PATH}{selection}.png')

    @commands.command(aliases=['addmemories', 'remember'])
    async def addmemory(self, ctx):
        await ctx.channel.purge(limit=1)
        img_types = ['.png', '.jpg', '.jpeg', '.gif']
        print('Attempting to save attachment...')
        if not ctx.message.attachments:
            await ctx.send('Please supply a link or attachment to save to memories.')
        else:
            for attachment in ctx.message.attachments:
                if (attachment.filename.lower().endswith(image) for image in img_types):
                    save_file = (
                        f'{MEMORY_PATH}{len(os.listdir(MEMORY_PATH))+1}.png')
                    await ctx.send('Attempting to save memory.')
                    await attachment.save(save_file)
                    await ctx.send(f'File saved as `{save_file}`.')
                else:
                    await ctx.send('Image type not supported.')

    @commands.command()
    async def memories(self, ctx):
        i = len(os.listdir(MEMORY_PATH))

        await ctx.send(f'I have {i} memories saved.')


def setup(client):
    client.add_cog(Memories(client))
    print(f'Loaded {os.path.basename(__file__)} successfully')


# await ctx.send(file=discord.File('./resources/tails.png'))
