from discord.ext import commands, tasks
import discord
from itertools import cycle


class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

    status = cycle(["your mom", "petni and the player", "my heartstrings", "your girl"])

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()
        print("status module has been launched")

    # background status changes
    @tasks.loop(minutes=5)
    async def change_status(self):
        await self.client.change_presence(activity=discord.Game(next(self.status)))

    # commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"ping: {round(self.client.latency * 1000)}")


def setup(client):
    client.add_cog(Status(client))
