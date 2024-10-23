import discord
import asyncio
from redbot.core import commands, Config, app_commands
from redbot.core.bot import Red
from discord.ext import tasks

class God(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=8542951920)
        self.config.register_guild(**default_guild)

    def has_higher_role(self, ctx, target: discord.Member):
        return ctx.author.top_role > target.top_role
  
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.hybrid_group(name="hakai", aliases=["hakai"])
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        if self.has_higher_role(ctx, member):
            try:
                await ctx.send('https://tenor.com/view/beerus-gif-20373634')
            except discord.HTTPException as error:
                await ctx.send(f'Error al enviar el gif: {error}')
            await asyncio.sleep(5)
            await member.ban(reason=f'Baneado por {ctx.author}')
            await ctx.send(f'{member.mention} ha sido baneado por {ctx.author}.')
        else:
            await ctx.send('No puedes banear a alguien con un rol igual o superior al tuyo.')
