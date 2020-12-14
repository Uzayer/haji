import json
import os

from discord.ext import commands

# loads token from a .json file
with open(r".\json_files\discord_token.json", "r") as read_file:
    dict_token = json.load(read_file)
    token = dict_token["token"]

client = commands.Bot(command_prefix="haji ")


@client.event
async def on_ready():
    print("Dipon Roy is ready to launch")


@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"loaded {extension}, ping: {round(client.latency * 1000)}")


@client.command()
async def unload(ctx, extension):
    await ctx.send(f"unloaded {extension}, ping: {round(client.latency * 1000)}")


@unload.error
async def unload_error(ctx, error, extension):
    if isinstance(error, commands.ExtensionNotLoaded):
        ctx.send(f"{extension} hasn't been loaded yet")


@client.command()
async def reload(ctx, extension):
    if extension is None:
        await ctx.send("USAGE: haji reload 'name of module without the quotes'")
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"reloaded {extension}, ping: {round(client.latency * 1000)}")


@reload.error
async def reload_error(ctx, error, extension):
    if isinstance(error, commands.ExtensionNotLoaded):
        ctx.send(f"{extension} hasn't been loaded yet")

        if not os.path.exists("./cache"):
            os.mkdir("./cache")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        # the [: -3] gets rid of ".py" from the filename
        client.load_extension(f"cogs.{filename[: -3]}")

client.run(token)
