import discord
from redbot.core import commands, Config, app_commands
from redbot.core.bot import Red
from discord.ext import tasks
from datetime import datetime, timedelta

class HomeworkCog(commands.Cog):
    """Un cog para gestionar un calendario de entregas de trabajos de clase"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"announcement_channel": None, "homework": []}
        self.config.register_guild(**default_guild)
        self.check_due_dates.start()

    @commands.guild_only()
    @commands.guildowner()
    @commands.hybrid_group(name="homeworkconfig", aliases=["hwconfig"])
    async def configuration(self, ctx: commands.Context):
        """Configuración del calendario de entregas."""
        pass

    @configuration.command(name="setchannel", aliases=["channelset"])
    async def set_announcement_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Configura el canal para anuncios de entregas."""
        await self.config.guild(ctx.guild).announcement_channel.set(channel.id)
        await ctx.send(f"Canal de anuncios configurado en {channel.mention}!")

    @configuration.command(name="addhomework", aliases=["addhw"], usage="<str> <str>")
    async def add_homework(self, ctx: commands.Context, title: str, due_date: str):
        """Añade una nueva entrega al calendario. El formato de la fecha es YYYY-MM-DD."""
        try:
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            await ctx.send("Formato de fecha inválido. Usa YYYY-MM-DD.")
            return

        # Agregar entrega a la base de datos
        async with self.config.guild(ctx.guild).homework() as homework_list:
            homework_list.append({"title": title, "due_date": due_date})

        await ctx.send(f"Entrega '{title}' añadida para el {due_date}!")

    @configuration.command(name="listhomework", aliases=["hwlist"])
    async def list_homework(self, ctx: commands.Context):
        """Muestra todas las entregas pendientes."""
        homework_list = await self.config.guild(ctx.guild).homework()
        if not homework_list:
            await ctx.send("No hay entregas pendientes.")
            return

        message = "**Lista de entregas pendientes:**\n"
        for hw in homework_list:
            message += f"- {hw['title']} (Fecha límite: {hw['due_date']})\n"
        await ctx.send(message)

    @tasks.loop(hours=24)
    async def check_due_dates(self):
        """Revisa las fechas de entrega y envía avisos si es necesario."""
        current_date = datetime.now().date()
        check_date = current_date + timedelta(days=1)

        for guild in self.bot.guilds:
            channel_id = await self.config.guild(guild).announcement_channel()
            if not channel_id:
                continue

            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            homework_list = await self.config.guild(guild).homework()

            # Buscar entregas con fecha límite mañana
            for hw in homework_list:
                due_date = datetime.strptime(hw['due_date'], '%Y-%m-%d').date()
                if due_date == check_date:
                    await channel.send(f"📢 Recordatorio: La entrega '{hw['title']}' es mañana ({due_date})!")

    @commands.guild_only()
    @commands.guildowner()
    @commands.hybrid_group(name="clearhomework", aliases=["hclear"])
    async def clear_homework(self, ctx: commands.Context):
        """Elimina todas las entregas del calendario."""
        await self.config.guild(ctx.guild).homework.set([])
        await ctx.send("Todas las entregas han sido eliminadas.")

    @check_due_dates.before_loop
    async def before_check_due_dates(self):
        await self.bot.wait_until_ready()

