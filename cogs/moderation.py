import discord
import os
import re
import asyncio
import shutil
from discord.ext import commands, tasks


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("moderation module has been launched")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.client.user.id:
            return
        if re.search("\.\.\.", message.content):
            mute_minutes = 5
            await message.channel.send(
                f"emne..kotha bolle....emnei....ban khaba...Ekhon {str(mute_minutes)} min chup thak")
            user = message.author
            muted_role = discord.utils.get(message.guild.roles, name="Muted")
            await user.add_roles(muted_role)
            await asyncio.sleep(mute_minutes * 60)
            await user.remove_roles(muted_role)

    # For some reason, the same command does not work with ctx instead of message
    # @commands.Cog.listener()
    # async def anti_riyasat(self, ctx):
    #     user = ctx.author
    #     if user.id == self.client.user.id:
    #         return
    #     if re.search("\.\.\.", ctx.message.content):
    #         await ctx.send("emne..kotha bolle....emnei....ban khaba...")
    #         muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    #         await user.add_roles(muted_role)

    # background status changes
    @tasks.loop(hours=2)
    async def clear_cache(self):
        await self.clearcache_no_ctx()

    # clearcache_no_ctx is auto cache clear command for the background task

    @commands.command()
    async def clearcache_no_ctx(self):
        cache_path = './cache/'
        for file in os.listdir(cache_path):
            cache_folder = os.path.join(cache_path, file)
            try:
                if os.path.isfile(cache_folder) or os.path.islink(cache_folder):
                    os.unlink(cache_folder)
                elif os.path.isdir(cache_folder):
                    shutil.rmtree(cache_folder)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (cache_folder, e))
        print("cache cleared bro")

    # clearcache command is for manual override to clear cache

    @commands.has_role("kodarr")
    @commands.command()
    async def clearcache(self, ctx):
        cache_path = './cache/'
        for file in os.listdir(cache_path):
            cache_folder = os.path.join(cache_path, file)
            try:
                if os.path.isfile(cache_folder) or os.path.islink(cache_folder):
                    os.unlink(cache_folder)
                elif os.path.isdir(cache_folder):
                    shutil.rmtree(cache_folder)
            except Exception as e:
                await ctx.send('Failed to delete %s. Reason: %s' % (cache_folder, e))
        await ctx.send("cache cleared bro")

    @clearcache.error
    async def clearcache_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I don't think you have the facilities for that big man")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("koyta clear korbo? give a number after clear")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("I don't think you have the facilities for that big man")


def setup(client):
    client.add_cog(Moderation(client))
