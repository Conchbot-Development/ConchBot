import discord
from discord.ext import commands
import sqlite3


class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_blacklist(self, id1):
        db = sqlite3.connect('./bot/db/config.db')
        cursor = db.cursor()

        cursor.execute(f"SELECT id FROM blacklist WHERE id = {id1}")
        result = cursor.fetchone()

        db.close()
        cursor.close()

        return result is not None

    async def check_ff(self, guild):
        db = sqlite3.connect('./bot/db/config.db')
        cursor = db.cursor()
        cursor.execute(f"SELECT familyfriendly FROM config WHERE guild_id = {guild.id}")
        check = cursor.fetchone()
        if check is None:
            cursor.execute(f"SELECT guild_id FROM config WHERE guild_id = {guild.id}")
            check0 = cursor.fetchone()
            if check0 is None:
                cursor.execute(f"INSERT INTO config (guild_id, familyfriendly) VALUES ({guild.id}, 0)")
            else:
                cursor.execute(f"UPDATE config SET familyfriendly = 0 WHERE guild_id = {guild.id}")
            db.commit()
            cursor.close()
            db.close()
            return "Inactive"
        if check[0] == 1:
            return "Active"
        elif check[0] == 0:
            return "Inactive"
        elif check[0] == 2:
            return "fuf"

    @commands.group(invoke_without_command=True, disabled=True)
    async def config(self, ctx):
        embed = discord.Embed(title="Configuration Settings", colour=discord.Colour.gold())
        embed.add_field(name="Family Friendly Mode",
                        value=f"Status: {await self.check_ff(ctx.guild)}\n "
                              "DISCLAIMER: Family friendly mode does not apply to the "
                              "bot's AI function."
                        )
        await ctx.send(embed=embed)

    @config.command(disabled=True)
    async def ff(self, ctx):
        db = sqlite3.connect('./bot/db/config.db')
        cursor = db.cursor()
        status = await self.check_ff(ctx.guild)
        if status == "Active":
            await ctx.send("Family friendly mode is already active!")
        else:
            cursor.execute(f"UPDATE config SET familyfriendly = 1 WHERE guild_id = {ctx.guild.id}")
            await ctx.send("Family friendly mode now active!")
        db.commit()
        cursor.close()
        db.close()


def setup(client):
    client.add_cog(Config(client))
