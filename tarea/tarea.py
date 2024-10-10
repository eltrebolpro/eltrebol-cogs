import discord
from redbot.core import commands, Config, app_commands
from redbot.core.bot import Red
from discord.ext import tasks
from datetime import datetime, timedelta

class HomeworkCog(commands.Cog):
    """Un cog para gestionar un calendario de entregas de clase"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"canal_anuncios": None, "entregas": []}
        self.config.register_guild(**default_guild)
        self.revisar_fechas_entregas.start()

    @commands.guild_only()
    @commands.guildowner()
    @commands.hybrid_group(name="configentregas", aliases=["entregaconfig"])
    async def configuracion(self, ctx: commands.Context):
        """Configuración del calendario de entregas."""
        pass

    @configuracion.command(name="setcanal", aliases=["canalset"])
    async def set_canal_anuncios(self, ctx: commands.Context, canal: discord.TextChannel):
        """Configura el canal para anuncios de entregas."""
        await self.config.guild(ctx.guild).canal_anuncios.set(canal.id)
        await ctx.send(f"¡Canal de anuncios configurado en {canal.mention}!")

    @configuracion.command(name="añadirtarea", aliases=["addentrega"], usage="<str> <str>")
    async def añadir_entrega(self, ctx: commands.Context, titulo: str, fecha_entrega: str):
        """Añade una nueva entrega al calendario. El formato de la fecha es DD-MM-AA."""
        try:
            fecha_obj = datetime.strptime(fecha_entrega, '%d-%m-%y').date()
        except ValueError:
            await ctx.send("Formato de fecha inválido. Usa DD-MM-AA.")
            return

        async with self.config.guild(ctx.guild).entregas() as lista_entregas:
            lista_entregas.append({"titulo": titulo, "fecha_entrega": fecha_entrega})

        await ctx.send(f"¡Entrega '{titulo}' añadida para el {fecha_entrega}!")

    @configuracion.command(name="listartareas", aliases=["listentregas"])
    async def listar_entregas(self, ctx: commands.Context):
        """Muestra todas las entregas pendientes."""
        lista_entregas = await self.config.guild(ctx.guild).entregas()
        if not lista_entregas:
            await ctx.send("No hay entregas pendientes.")
            return

        mensaje = "**Lista de entregas pendientes:**\n"
        for entrega in lista_entregas:
            mensaje += f"- {entrega['titulo']} (Fecha límite: {entrega['fecha_entrega']})\n"
        await ctx.send(mensaje)

    @configuracion.command(name="eliminartarea", aliases=["borrarentrega"])
    async def eliminar_entrega(self, ctx: commands.Context, titulo: str):
        """Elimina una entrega específica del calendario."""
        async with self.config.guild(ctx.guild).entregas() as lista_entregas:
            for entrega in lista_entregas:
                if entrega['titulo'].lower() == titulo.lower():
                    lista_entregas.remove(entrega)
                    await ctx.send(f"La entrega '{titulo}' ha sido eliminada.")
                    return

            await ctx.send(f"No se encontró ninguna entrega con el título '{titulo}'.")

    @tasks.loop(hours=24)
    async def revisar_fechas_entregas(self):
        """Revisa las fechas de entrega y envía avisos si es necesario."""
        fecha_actual = datetime.now().date()
        fecha_aviso = fecha_actual + timedelta(days=1)

        for guild in self.bot.guilds:
            canal_id = await self.config.guild(guild).canal_anuncios()
            if not canal_id:
                continue

            canal = self.bot.get_channel(canal_id)
            if not canal:
                continue

            lista_entregas = await self.config.guild(guild).entregas()

            # Buscar entregas con fecha límite mañana
            for entrega in lista_entregas:
                fecha_entrega = datetime.strptime(entrega['fecha_entrega'], '%d-%m-%y').date()
                if fecha_entrega == fecha_aviso:
                    await canal.send(f"📢 Recordatorio: La entrega '{entrega['titulo']}' es mañana ({entrega['fecha_entrega']})!")

    @commands.guild_only()
    @commands.guildowner()
    @commands.hybrid_group(name="limpiartareas", aliases=["clearentregas"])
    async def limpiar_entregas(self, ctx: commands.Context):
        """Elimina todas las entregas del calendario."""
        await self.config.guild(ctx.guild).entregas.set([])
        await ctx.send("Todas las entregas han sido eliminadas.")

    @revisar_fechas_entregas.before_loop
    async def antes_revisar_fechas(self):
        await self.bot.wait_until_ready()
