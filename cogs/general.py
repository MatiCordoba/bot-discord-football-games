import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["ayuda"])
    async def mostrar_info(self, ctx):
        await self.enviar_info(ctx)

    async def enviar_info(self, ctx):
        embed = discord.Embed(
            title="🎮 Bot de Juegos de Fútbol | ⚽ FutBot Juegos",
            description="Jugá en grupo con comandos simples y partidas por turnos.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="🎲 Juegos disponibles",
            value=(
                "• `adivina-jugador` – ¿Quién soy? versión fútbol ⚽\n"
                "• `impostor` – Impostor versión fútbol ⚽\n"
                "• (Próximamente más juegos... 🧩)"
            ),
            inline=False
        )

        embed.add_field(
            name="🧾 Comandos globales",
            value=(
                "`!empezar {juego}` → Inicia una partida\n"
                "`!terminar` → Cancela la partida actual\n"
                "`!reglas {juego}` → Muestra las reglas del juego\n"
                "`!info` o `!ayuda` → Muestra esta ayuda"
            ),
            inline=False
        )

        embed.add_field(
            name="📌 Tip",
            value="Probá con `!reglas adivina-jugador` para aprender a jugar.",
            inline=False
        )

        embed.set_footer(text="Bot creado por Matías / orfeo.dev")
        await ctx.send(embed=embed)


    @commands.command(name="reglas")
    async def mostrar_reglas(self, ctx, juego: str = None):
        if juego is None:
            await ctx.send(
                "ℹ️ Especificá un juego para ver sus reglas.\n"
                "Ejemplo: `!reglas adivina-jugador`\n\n"
                "🎮 Juegos disponibles:\n"
                "- `adivina-jugador`"
            )
            return

        juego = juego.lower().strip()

        if juego == "adivina-jugador":
            embed = discord.Embed(
                title="📜 Reglas de Adivina-jugador",
                description="¿Quién soy? versión fútbol",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="🎯 Objetivo",
                value="Adivinar qué jugador de fútbol te tocó, haciendo preguntas de sí o no.",
                inline=False
            )
            embed.add_field(
                name="🧠 Cómo se juega",
                value=(
                    "1. Cada jugador recibe un nombre oculto que el resto sí conoce.\n"
                    "2. Por turnos, hacés preguntas con `!pregunta` (ej: ¿Soy argentino?).\n"
                    "3. En tu turno, podés adivinar con `!adivinar Messi`.\n"
                    "4. El juego termina cuando 3 jugadores adivinan correctamente.\n"
                    "5. Se juega por voz o chat, respondiendo sí/no entre todos."
                ),
                inline=False
            )
            embed.set_footer(text="Bot creado por Matías / orfeo.dev")
            await ctx.send(embed=embed)
        
        elif juego == "impostor":
            embed = discord.Embed(
                title="🎭 Reglas de Impostor",
                description="Un jugador oculto entre ustedes... ¿podrán descubrirlo?",
                color=discord.Color.red()
            )
            embed.add_field(
                name="🎯 Objetivo",
                value="Descubrir quién es el impostor entre los jugadores antes de que sea tarde.",
                inline=False
            )
            embed.add_field(
                name="🧠 Cómo se juega",
                value=(
                    "1. Todos los jugadores reciben un jugador de fútbol real por mensaje privado.\n"
                    "2. Uno de los jugadores será el **IMPOSTOR** y no recibirá el nombre.\n"
                    "3. En cada ronda, todos dicen una palabra relacionada con el jugador (con `!palabra algo`).\n"
                    "4. Luego se vota con `!voto @usuario` para expulsar a quien sospechen.\n"
                    "5. Si el impostor es expulsado → ganan los demás.\n"
                    "6. Si se expulsa a un inocente → sigue el juego. Si quedan 2 → gana el impostor."
                ),
                inline=False
            )
            embed.set_footer(text="Bot creado por Matías / orfeo.dev")
            await ctx.send(embed=embed)

        else:
            await ctx.send("❌ Juego no reconocido. Probá con `!reglas` para ver la lista.")

async def setup(bot):
    await bot.add_cog(General(bot))
