import discord
from discord.ext import commands
import unidecode
import random
import json

class AdivinaJugador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.partidas = {}
        with open("data/jugadores.json", "r", encoding="utf-8") as f:
            self.jugadores = json.load(f)

    @commands.command(name="empezar_adivinar")
    async def empezar_impostor(self, ctx, juego: str = None):
        if juego != "adivinar":
            await ctx.send("Juego no reconocido. Por ahora solo tenemos `adivinar` e `impostor`.")
            return

        miembros = [m for m in ctx.guild.members if not m.bot]

        if len(miembros) < 1:
            await ctx.send("No hay jugadores disponibles.")
            return

        # ⚠️ TEST MODE: si solo hay 1 jugador, se duplica para simular partida
        if len(miembros) == 1:
            miembros = miembros * 2
            await ctx.send("⚠️   Modo test: duplicando jugador para simular partida.")

        # Asignar un jugador aleatorio a cada miembro, usando alias
        asignaciones = {}
        for m in miembros:
            jugador_elegido = random.choice(self.jugadores)
            asignaciones[m.id] = jugador_elegido
        turno = [m.id for m in miembros]

        for miembro in miembros:
            jugador_asignado = asignaciones[miembro.id]
            mensaje = f"🎯   `{miembro.display_name}` tiene que adivinar: **{jugador_asignado['nombre']}**"
            for otro in miembros:
                if otro.id != miembro.id:
                    try:
                        await otro.send(mensaje)
                    except:
                        await ctx.send(f"No pude enviar DM a {otro.display_name}. Verifiquen que tengan los DMs habilitados.")

        self.partidas[ctx.guild.id] = {
            "asignaciones": asignaciones,
            "turno": turno,
            "indice_turno": 0,
            "acertaron": set(),
            "activo": True,
            "preguntas": {},
        }

        primer_nombre = ctx.guild.get_member(turno[0]).display_name
        await ctx.send(f"Juego iniciado. Es turno de **{primer_nombre}**. Escribí `!pregunta` o `!adivinar`.")

    @commands.command(name="pregunta")
    async def hacer_pregunta(self, ctx, *, pregunta: str):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or not partida["activo"]:
            await ctx.send("No hay un juego activo. Usá `!empezar adivina-jugador`.")
            return

        turno_id = partida["turno"][partida["indice_turno"]]
        if ctx.author.id != turno_id:
            await ctx.send("No es tu turno.")
            return

        await ctx.send(f"❓   Pregunta de **{ctx.author.display_name}**: *{pregunta}* → Respondan por voz o en el chat.")
        uid = ctx.author.id
        if uid not in partida["preguntas"]:
            partida["preguntas"][uid] = []
        partida["preguntas"][uid].append(pregunta)
        await self.pasar_turno(ctx)

    @commands.command(name="preguntas_adivinar")
    async def preguntas_adivinar(self, ctx):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or not partida["activo"]:
            await ctx.send("❌ No hay un juego activo de *Adivinar*.")
            return

        preguntas_dict = partida.get("preguntas", {})
        preguntas_usuario = preguntas_dict.get(ctx.author.id, [])

        if not preguntas_usuario:
            await ctx.send("❓ No hiciste ninguna pregunta todavía.")
            return

        texto = f"📋 **Tus preguntas hasta ahora, {ctx.author.display_name}:**\n"
        texto += "\n".join(f"{i+1}. {p}" for i, p in enumerate(preguntas_usuario))
        await ctx.send(texto)

    @commands.command(name="adivinar")
    async def adivinar_jugador(self, ctx, *, nombre: str):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or not partida["activo"]:
            await ctx.send("No hay un juego activo. Usá `!empezar adivina-jugador`.")
            return

        turno_id = partida["turno"][partida["indice_turno"]]
        if ctx.author.id != turno_id:
            await ctx.send("No es tu turno.")
            return

        # Cambiar asignado a objeto y extraer nombre y alias
        asignado_obj = partida["asignaciones"].get(ctx.author.id)
        if not asignado_obj:
            await ctx.send("No estás en esta partida.")
            return
        asignado = asignado_obj["nombre"]
        aliases = asignado_obj.get("alias", [])
        if isinstance(aliases, str):
            aliases = [aliases]  # Soporte retrocompatibilidad

        # Normalización de alias
        def normalizar(texto):
            return unidecode.unidecode(texto.lower().strip())

        input_normalizado = normalizar(nombre)
        asignado_normalizado = normalizar(asignado)
        alias_normalizados = [normalizar(a) for a in aliases]

        acertado = False

        # Caso 1: nombre completo o alias coincide
        if input_normalizado in alias_normalizados or input_normalizado == asignado_normalizado:
            acertado = True

        else:
            # Caso 2: intento con apellido completo (últimas 2 o más palabras del nombre)
            partes_asignado = asignado_normalizado.split()
            posibles_apellidos = [" ".join(partes_asignado[-i:]) for i in range(1, 4)]  # último 1, 2, o 3 palabras
            apellido_jugador = posibles_apellidos[-1]  # último 2 o 3 palabras, ej: "di maria", "van dijk"

            if input_normalizado == apellido_jugador:
                jugadores_con_mismo_apellido = [
                    j for j in self.jugadores if normalizar(j["nombre"]).endswith(apellido_jugador)
                ]
                if len(jugadores_con_mismo_apellido) == 1:
                    acertado = True
                else:
                    await ctx.send(
                        f"⚠️   Hay más de un jugador con el apellido **{apellido_jugador.capitalize()}**. Especificá el nombre completo."
                    )
                    return

        # 🔄 Caso especial: permiten adivinar sin el "Jr"
        if not acertado and asignado_normalizado.endswith(" jr"):
            sin_jr = asignado_normalizado.replace(" jr", "").strip()
            if input_normalizado == sin_jr:
                acertado = True

        if acertado:
            partida["acertaron"].add(ctx.author.id)
            await ctx.send(f"🎉   ¡{ctx.author.display_name} adivinó correctamente: **{asignado}**!")
        else:
            await ctx.send(f"❌   {ctx.author.display_name} se equivocó. No sos **{nombre}**.")

        if len(partida["acertaron"]) >= 3:
            partida["activo"] = False
            ganadores = [
                ctx.guild.get_member(uid).display_name for uid in partida["acertaron"]
            ]
            await ctx.send(f"🏁   Fin del juego. Adivinaron correctamente: {', '.join(ganadores)}")
            return

        await self.pasar_turno(ctx)

    async def pasar_turno(self, ctx):
        partida = self.partidas[ctx.guild.id]
        jugadores = partida["turno"]
        total = len(jugadores)

        for _ in range(total):
            partida["indice_turno"] = (partida["indice_turno"] + 1) % total
            siguiente_id = jugadores[partida["indice_turno"]]
            if siguiente_id not in partida["acertaron"]:
                siguiente = ctx.guild.get_member(siguiente_id)
                await ctx.send(f"➡️   Turno de **{siguiente.display_name}**. Usá `!pregunta` o `!adivinar`.")
                return

        await ctx.send("No quedan más jugadores en juego.")

    @commands.command(name="terminar_adivinar")
    async def terminar_adivinar(self, ctx, juego: str = None):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or not partida["activo"]:
            await ctx.send("No hay ningún juego activo en este momento.")
            return

        self.partidas[ctx.guild.id]["activo"] = False
        await ctx.send("🛑   El juego ha sido cancelado manualmente.")

async def setup(bot):
    await bot.add_cog(AdivinaJugador(bot))
