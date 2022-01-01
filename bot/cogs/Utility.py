import os
import platform
import datetime
import discord
from discord.ext import commands
import sqlite3
import inspect
import os
import time
from jishaku.codeblocks import codeblock_converter

start_time = time.time()


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    async def get_update_info(self, version=None):
        db = sqlite3.connect("./bot/db/updates.db")
        cursor = db.cursor()

        if version is None:
            cursor.execute("SELECT MAX(version) FROM updates")
            result = cursor.fetchone()
            version = result[0]
        cursor.execute(f"SELECT name FROM updates WHERE version = '{version}'")
        name = cursor.fetchone()
        cursor.execute(f"SELECT desc FROM updates WHERE version = '{version}'")
        desc = cursor.fetchone()
        cursor.execute(f"SELECT updates FROM updates WHERE version = '{version}'")
        updates = cursor.fetchone()
        cursor.execute(f"SELECT published FROM updates WHERE version = '{version}'")
        published = cursor.fetchone()

        cursor.close()
        db.close()        

        return version, name[0], desc[0], updates[0], published[0]

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            colour=discord.Colour.dark_red(),
            title=f"Pong! **__{round(self.client.latency * 1000)}__**"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def guilds(self, ctx):
        servers = list(self.client.guilds)
        embed = discord.Embed(title="Guilds", colour=ctx.author.colour)
        for x in range(len(servers)):
            embed.add_field(name=servers[x-1].name, value=servers[x-1].member_count, inline=False)
        embed.add_field(name="Total Guilds:", value=len(self.client.guilds))
        embed.add_field(name="Total Members:", value=len(set(self.client.get_all_members())))
        await ctx.send(embed=embed)
        await ctx.send(f"Total Guilds: {len(self.client.guilds)}\nTotal Members: {len(set(self.client.get_all_members()))}")

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        await ctx.send({len(self.client.guilds)})

    @commands.command()
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        e = discord.Embed(title='Uptime,', color=discord.Color.green())
        e.add_field(name="Time:", value=f"{days}**d**, {hours}**h**, {minutes}**m**, {seconds}**s**", inline=True)
        e.add_field(name="Time Lapse:", value=text, inline=False)
        await ctx.send(embed=e)

    @commands.command(aliases=["purge"])
    @commands.cooldown(1, 5, commands.BucketType.user) 
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount:int):
        if amount < 1:
            await ctx.send("You can't clear a negative amount.")
        embed = discord.Embed(
            colour = discord.Colour.purple(),
        )
        embed.add_field(name="Messages Cleared", value=f"{amount} messages cleared.")

        await ctx.channel.purge(limit=amount+1)
        await ctx.send(embed=embed, delete_after=5)
    
    @commands.command(aliases=["statistics", "info", "information"])
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def stats(self, ctx):
        delta_uptime = datetime.datetime.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(title=f'{self.client.user.name} Stats', colour=ctx.author.colour)
        embed.add_field(name="Bot Name:", value=self.client.user.name)
        embed.add_field(name="Bot Id:", value=self.client.user.id)
        embed.add_field(name="Total Guilds:", value=len(self.client.guilds))
        embed.add_field(name="Total Users:", value=len(set(self.client.get_all_members())))
        embed.add_field(name="Total Commands:", value=len(set(self.client.commands)))
        embed.add_field(name="Total Cogs:", value=len(set(self.client.cogs)))
        embed.add_field(name="Uptime:", value=f"{days}**d**, {hours}**h**, {minutes}**m**, {seconds}**s**", inline=True)
        embed.add_field(name="Uptime Lapse:", value=text)
        await ctx.send(embed=embed)


    @commands.command(aliases=["github", "code"])
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def source(self, ctx, *, command_name=None):
        # Source code of ConchBot github page
        conchbot_source_code_url = self.client.getenv("GITHUB_REPO_LINK")

        # Branch of ConchBot github page
        branch = self.client.getenv("GITHUB_REPO_BRANCH")

        embed = discord.Embed(title="ConchBot Source Code")

        # If Command Parameter is None
        if command_name is None:
            embed.add_field(name="Source:", value=conchbot_source_code_url, inline=False)
        else:
            # Get the command
            obj = self.client.get_command(command_name.replace('.', ' '))

            # If command cannot be found
            if obj is None:
                await ctx.send('Could not find command in my github source code.')

            # Get the source of the code
            src = obj.callback.__code__

            # Check if its a module
            module = obj.callback.__module__

            # Get the file name
            filename = src.co_filename

            # Check if module doesn't start with discord
            if not module.startswith('discord'):
                location = os.path.relpath(filename).replace('\\', '/')
            else:
                location = module.replace('.', '/') + '.py'

            # Get the line of code for the command
            end_line, start_line = inspect.getsourcelines(src)

            # Go to the command url. Note: It is a permalink
            final_url = (f'{conchbot_source_code_url}/blob/{branch}/{location}#L{start_line}-L'
                     f'{start_line + len(end_line) - 1}')

            embed.add_field(name="Command Source:", value=final_url, inline=False)

        embed.set_footer(icon_url=ctx.author.avatar.url, text=f"Requested {ctx.author.name}#{ctx.author.discriminator}")
        await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx):
        check = ctx.author.guild_permissions.kick_members
        if check is True or ctx.author.id == 579041484796461076:
            await ctx.send("Are you sure you want me to leave the server? `yes` or `no.`")
            msg = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            if "yes" in msg.content.lower():
                await ctx.send("I'm sorry you don't want me here anymore. If there was a problem or annoyance, you"
                " can feel free to join my support server. (https://discord.gg/PyAcRfukvc)")
                await ctx.guild.leave()
            elif "no" in msg.content.lower():
                await ctx.send("Thanks for deciding to keep me!")
            else:
                await ctx.send("Incorrect value. Aborting...")
        else:
            await ctx.send("You don't have permissions to make me leave!")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must specify an amount of messages to clear.")
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the permissions required to purge messages.")
            return
        if isinstance(error, commands.errors.BadArgument):
            await ctx.send("Your amount must be an integer greater than one.")
            return
        

    
    
    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def blacklist(self, ctx, val=None):
        if val is not None:
            await ctx.invoke(self.client.get_command(f'blacklist add {val}'))
        else:
            return await ctx.send("You can add or remove")
    
    @blacklist.command()
    async def add(self, ctx, id=None):
        if id is None:
            await ctx.send("You need the id of that user")
        else:
            db = sqlite3.connect("./bot/db/config.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT id FROM blacklist WHERE id = {id}")
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f"INSERT INTO blacklist (id) VALUES ({id})")
                await ctx.send("Member blacklisted.")
            else:
                await ctx.send("That Member is already blacklisted.")
            db.commit()
            cursor.close()
            db.close()

    @blacklist.command()
    async def remove(self, ctx, id):
        if id is None:
            await ctx.send("You need the id of that user")
        else:
            db = sqlite3.connect("./bot/db/config.db")
            cursor = db.cursor()
            cursor.execute(f"SELECT id FROM blacklist WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            blacklisted = result[0]
            if id not in blacklisted:
                await ctx.send("That ID is not blacklisted.")
            else:
                cursor.execute(f"DELETE FROM blacklist WHERE guild_id = {ctx.guild.id}")
                await ctx.send("ID removed from blacklist.")
            db.commit()
            cursor.close()
            db.close()

def setup(client):
    client.add_cog(Utility(client))
