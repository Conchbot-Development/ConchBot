import discord
from discord.ext import commands
import datetime
import sqlite3
import asyncio


class Sniping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
        self.check_db = self.check_db()
        self.db = sqlite3.connect("./bot/db/snipe.db")
        self.cursor = self.db.cursor()
        
    def snipe_embed(self, db_type):
        return discord.Embed(title=f"{db_type.capitalize()} Snipes", colour=discord.Color.green())
    
    async def get_data(self, db_type, guildid, num, ctx = None):
        db_type = str(db_type).lower()

        embed = self.snipe_embed(db_type)

        if db_type == "delete":
            db_type = "delete_snipes"
        elif db_type == "edit":
            db_type = "edit_snipes"
        elif db_type == "reaction":
            db_type = "reaction_snipes"
        
        self.cursor.execute(f"SELECT * FROM {db_type} WHERE guild_id = {guildid}")
        result = self.cursor.fetchall()
        
        result1 = result
        
        try:
            result = result[num]
        except IndexError:
            return embed.add_field(name="No more data was found", value="No snipe data found.")
        
        num = 1 if num == 0 else num

        if db_type == 'delete_snipes':
            embed = await self.delete_embed(embed, result, num, result1)

        elif db_type == 'edit_snipes':
            embed = await self.edit_embed(embed, result, num, result1)
            
        elif db_type == 'reaction_snipes':
            embed = await self.reaction_embed(ctx, embed, result, num, result1)

        return embed
    
    async def delete_embed(self, embed, result, num, result1):
        channel = self.bot.get_channel(int(result[1]))
        message_content = result[2]
        author = self.bot.get_user(int(result[3]))
        attachments = result[4]
        time = result[5]
        
        message_content = self._unconvert_quotes(message_content)        

        embed.add_field(name="Channel", value=f"{channel.mention}")
        embed.add_field(name="Message Content", value=f"{message_content}")
        embed.add_field(name="Author", value=f"{author.mention}")
        if ',' in attachments:
            self._attachments(attachments, embed)
        else:
            embed.set_image(url=attachments)
        self._footer(result1, embed, author, num)
        return self._fields(embed, time, author)
        
    async def edit_embed(self, embed, result, num, result1):
        print(result)
        author = self.bot.get_user(int(result[1]))
        channel = self.bot.get_channel(int(result[2]))
        
        before_content = result[3]
        after_content = result[4]
        jump_url = result[5]
        time = result[6]
        
        before_content = self._unconvert_quotes(before_content)
        after_content = self._unconvert_quotes(after_content)
        

        embed.add_field(name="Author", value=f"{author.mention}")
        embed.add_field(name="Channel", value=f"{channel.mention}")
        embed.add_field(name="Before Edit", value=f"{before_content}")
        embed.add_field(name="After Edit", value=f"{after_content}")
        embed.add_field(name="Jump URL", value=f"[Click me!]({jump_url})")
        self._footer(result1, embed, author, num)
        return self._fields(embed, time, author)
    
    async def reaction_embed(self, ctx, embed, result, num, result1):
        channel = self.bot.get_channel(int(result[1]))
        emoji = result[2]
        jump_url = result[3]
        author = self.bot.get_user(int(result[4]))
        time = result[5]
        
        message_id = jump_url.split('/')[-1]  
        message = await ctx.fetch_message(message_id)
        
        message_content = message.content
        attachments = self._attachment(message.attachments)
        
        message_content = await self._check_text(message_content, 926180891577962577, 'message')
        message_content = self._unconvert_quotes(message_content)
        
        
        embed.add_field(name="Channel", value=f"{channel.mention}")
        embed.add_field(name="Message Content", value=f"{message_content}")
        embed.add_field(name="Author", value=f"{author.mention}")
        embed.add_field(name="Emoji", value=f"{emoji}")
        embed.add_field(name="Jump URL", value=f"[Click me!]({jump_url})")
        embed.add_field(name="Time", value=f"{time}")
        if ',' in attachments:
            self._attachments(attachments, embed)
        else:
            embed.set_image(url=attachments)
        self._footer(result1, embed, author, num)
        return self._fields(embed, time, author)

    def _attachments(self, attachments, embed):
        attachments = list(attachments.split(','))
        attachments = '\n'.join(attachments)
        embed.add_field(name='Attachment', value=f'{attachments}')
        
    def _format_file(self, file, text):
        with open(f'./bot/src/{file}.txt', 'w') as f:
            f.write(text)
            
        file = discord.File(f'./bot/src/{file}.txt')
        return file
        

    def _fields(self, embed, time, author):
        embed.add_field(name='Time', value=f'{time}')
        embed.set_thumbnail(url=author.avatar.url)
        return embed
    
    def _footer(self, result, embed, author, num):
        pages = self._check_pages(result)
        embed.set_footer(text=f"Requested by {author} | Page {num}/{pages}")
        return embed
    
    def _attachment(self, attachments):
        attachments = None if attachments is None else [attachment.url for attachment in attachments]
        attachments = None if attachments is None else ",".join(attachments)
        return attachments
    
    def _check_pages(self, result):
        for x in result:
            pages = len(result) if isinstance(x, (list, tuple)) else 1
            break
        return pages

    def _convert_quotes(self, text):
        text = text.replace('"', 'U+0022')
        text = text.replace("'", "U+0027")
        return text
    
    def _unconvert_quotes(self, text):
        text = text.replace('U+0022', '"')
        text = text.replace("U+0027", "'")
        return text
    
    async def _check_text(self, text, channel_id, filename):
        return (
            await self._upload_file(channel_id, filename, text)
            if len(text) > 1024
            else self._convert_quotes(text)
        )
        
    async def _upload_file(self, channel_id, filename, text):
        file = self._format_file(filename, text)
        message = await self.bot.get_channel(channel_id).send(file=file)
        return f"[View file]({message.attachments[0].url})"
    
    def emoji_to_unicode(self, emoji):
        return emoji.encode('utf-8')
    
    def check_db(self):
        connect = sqlite3.connect("bot/db/snipe.db")
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS delete_snipes (
            guild_id TEXT,
            channel TEXT,
            message_content TEXT,
            author TEXT,
            attachments TEXT,
            time TEXT
        )''')
        connect.commit()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS edit_snipes (
            guild_id TEXT,
            author TEXT,
            channel TEXT,
            before_content TEXT,
            after_content TEXT,
            jump_url TEXT,
            time TEXT
        )
        ''')
        connect.commit()

        
        cursor.execute('''CREATE TABLE IF NOT EXISTS reaction_snipes (
            guild_id TEXT,
            channel TEXT, 
            emoji TEXT,
            jump_url TEXT, 
            author TEXT, 
            time TEXT
        )''')
        
        connect.commit()
            
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        connect = sqlite3.connect("bot/db/snipe.db")
        cursor = connect.cursor()
                
        channel = message.channel.id
        message_content = message.content
        author = message.author.id
        attachments = self._attachment(message.attachments)
        guild_id = message.guild.id
        
        message_content = await self._check_text(message_content, 926180891577962577, 'message')

        sql = ('INSERT INTO delete_snipes (guild_id, channel, message_content, author, attachments, time) VALUES (?, ?, ?, ?, ?, ?)')
        value = (guild_id, channel, message_content, author, attachments, self.time)

        cursor.execute(
            sql, value
        )

        connect.commit()
        
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        connect = sqlite3.connect("bot/db/snipe.db")
        cursor = connect.cursor()
        
        author = before.author.id
        channel = before.channel.id
        before_content = before.content
        after_content = after.content
        jump_url = after.jump_url
        guild_id = before.guild.id
        
        before_content = await self._check_text(before_content, 926180891577962577, 'before')
        after_content = await self._check_text(after_content, 926180891577962577, 'after')
        
        sql = ("INSERT INTO edit_snipes (guild_id, author, channel, before_content, after_content, jump_url, time) VALUES (?, ?, ?, ?, ?, ?, ?)")
        value = (guild_id, author, channel, before_content, after_content, jump_url, self.time)
        
        cursor.execute(
            sql, value
        )
        
        connect.commit()
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        connect = sqlite3.connect("bot/db/snipe.db")
        cursor = connect.cursor()

        channel = payload.channel_id
        guild_id = payload.guild_id
        message_id = payload.message_id
        print(payload.emoji)
        emoji = self.emoji_to_unicode(f'{payload.emoji}')
        jump_url = f"https://discordapp.com/channels/{guild_id}/{channel}/{message_id}"
        author = payload.user_id

        
        sql = ("INSERT INTO reaction_snipes (guild_id, channel, emoji, jump_url, author, time) VALUES (?, ?, ?, ?, ?, ?)")
        value = (guild_id, channel, emoji, jump_url, author, self.time)

        cursor.execute(
            sql, value
        )

        connect.commit()
        
    
    @commands.group(invoke_without_command=True)
    async def snipe(self, ctx, number: int = 0):
        if number < 0:
            return await ctx.send("Please enter a valid number.")
        number = 0 if number in {0, 1} else number - 1
        
        embed = await self.get_data('delete', ctx.guild.id, number)
        await ctx.send(embed=embed)
        
    
    @snipe.command()
    async def delete(self, ctx, number: int = 0):
        if number < 0:
            return await ctx.send("Please enter a valid number.")
        number = 0 if number in {0, 1} else number - 1
        
        embed = await self.get_data('delete', ctx.guild.id, number)
        await ctx.send(embed=embed)
    
    @snipe.command()
    async def edit(self, ctx, number: int = 0):
        if number < 0:
            return await ctx.send("Please enter a valid number.")
        number = 0 if number in {0, 1} else number - 1
        
        embed = await self.get_data('edit', ctx.guild.id, number)
        await ctx.send(embed=embed)
    
    @snipe.command()
    async def reaction(self, ctx, number: int = 0):
        if number < 0:
            return await ctx.send("Please enter a valid number.")
        number = 0 if number in {0, 1} else number - 1
          
        embed = await self.get_data('reaction', ctx.guild.id, number, ctx)
        await ctx.send(embed=embed)
    
        
def setup(bot):
    bot.add_cog(Sniping(bot))