import discord
        
class Paginator(discord.ui.View): 
    def __init__(self, ctx, embeds): 
        super().__init__() 
        self.embeds = embeds
        self.ctx = ctx
        self.current_page = 0

    async def show_page(self, inter, page: int):
        self.current_page = 0 if page > len(self.embeds) else page
        embed = self.embeds[self.current_page]
        await inter.edit_original_message(embed=embed)
        
    @discord.ui.button(label='⏪')
    async def begining(self, button, inter):
        await inter.response.defer()
        await self.show_page(inter, 0)

    @discord.ui.button(label="⬅️")
    async def back(self, button, inter):
        await inter.response.defer()
        await self.show_page(inter, self.current_page - 1) 

    @discord.ui.button(label="➡️")
    async def move(self, button, inter):
        await inter.response.defer()
        await self.show_page(inter, self.current_page + 1)
        
    @discord.ui.button(label='⏩')
    async def end(self, button, inter):
        await inter.response.defer()
        await self.show_page(inter, -1)
        
    @discord.ui.button(label="Quit")
    async def quit(self, button, inter):
        await inter.response.defer()
        await inter.delete_original_message()    
        
    async def interaction_check(self, inter):
        if inter.user == self.ctx.author:
            return True
        await inter.response("Hey! You can't do that!", ephemeral=True)
        return False