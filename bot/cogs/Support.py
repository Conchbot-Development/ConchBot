import sqlite3
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv
import os
from bot.cogs.Currency import Currency


env = load_dotenv()


class Support(commands.Cog):
    def __init__(self, client):
        self.client = client
    

    @commands.command(description="Displays an embed of where you can get support for ConchBot.")
    async def support(self, ctx):
        embed = discord.Embed(
            title="ConchBot Support",
            colour=discord.Colour.gold()
        )
        embed.add_field(name="You Just Used the Support Command!", value="This means you either have a question about ConchBot,"
        " would like to report an error or bug, or just want to join the ConchBot community!")
        embed.add_field(name="ConchBot Discord Server", value="You can join ConchBot's support server [here](https://discord.gg/PyAcRfukvc)")
        embed.add_field(name="Or, if you don't want to join a server...", value="You can submit bugs or errors via 'cb report {description of bug}.")
        await ctx.send(embed=embed)
    
    @commands.command(description="Report a bug to the ConchBot developers.")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def report(self, ctx, *, content):
        channel = self.client.get_channel(795711741606101024)
        db = sqlite3.connect('./bot/db/config.db')
        cursor = db.cursor()
        cursor.execute('SELECT num FROM bugnum WHERE placeholder = 1')
        result = cursor.fetchone()
        num = result[0]+1
        embed = discord.Embed(
            title=f"Bug Report #{num}",
            colour=discord.Colour.red()
        )
        embed.add_field(name="Submitted By:", value=ctx.author)
        embed.add_field(name="Bug Description:", value=content)
        embed.set_footer(text=f"User ID: {ctx.author.id}")
        cursor.execute(f'UPDATE bugnum SET num = {num} WHERE placeholder = 1')
        await channel.send(embed=embed)
        await ctx.send("Thank you for the bug report! Our team will identify and fix the problem as soon as possible!")
        db.commit()
        cursor.close()
        db.close()

    # @commands.command()
    # @commands.is_owner()
    # async def respond(self, ctx, *, content):
    #     user, content = content.split(':;')

    #     user = self.client.get_user(user.id)

    #     if user is None:
    #         return await ctx.send("Failed.")

    #     embed=discord.Embed(title="Bug Report Response", color=discord.Color.random(), description="*You are receiving this message because you have recently submitted a bug about ConchBot.*")
    #     embed.add_field(name="Response:", value=content)
    #     embed.set_footer(text="*If this response asks for more information, you can just use the report command again.*")

    #     await user.send(embed=embed)

    #     await ctx.send("User contacted.")

    @commands.command(description="Suggest a feature!")
    @commands.cooldown(1, 86400, BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        channel = self.client.get_channel(819029394534039604)
        if channel is None:
            await ctx.guild.create_text_channel('suggestions')
            channel = discord.utils.get(ctx.guild.channels, name="suggestions")
        if len(suggestion)>100:
            await ctx.send("Please keep your suggestion under 100 characters as to not flood the suggestions channel.")
        elif len(suggestion)<10:
            await ctx.send("That suggestion is too short. Your suggestion must be more than 10 characters long.")
        else:
            embed = discord.Embed(
                title=f"{ctx.author.name}#{ctx.author.discriminator} has a suggestion!",
                colour=ctx.author.colour
            )
            embed.add_field(name="Submitted by:", value=ctx.author.name)
            embed.add_field(name="Suggestion:", value=suggestion)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send("Your suggestion has been submitted!")
            suggestion_message = await channel.send(embed=embed)
            await suggestion_message.add_reaction("⬆️")
            await suggestion_message.add_reaction("⬇️")

    @commands.command(description="Get a link to invite ConchBot to your server!")
    async def invite(self, ctx):
        embed = discord.Embed(
            title="ConchBot Invites",
            colour=ctx.author.colour
        )
        embed.add_field(name="ConchBot Invite:", value="You can invite ConchBot to your server "
        "[here](https://discord.com/api/oauth2/authorize?client_id=890362614155194428&permissions=2348927041&scope=applications.commands%20bot)")
        embed.add_field(name="Support Server Invite:", value="You can join ConchBot Support "
        "[here](https://discord.gg/PyAcRfukvc)")
        embed.add_field(name="ConchBot's creator (UnsoughtConch)'s community server:",
        value="You can join Conch's community server [here](https://discord.gg/n8XyytfxMk)")
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Support(client))
