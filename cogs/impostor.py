import discord
from discord.ext import commands
import random
import json
import unidecode

class Impostor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.partidas = {}  # key = guild.id

        with open("data/jugadores.json", "r", encoding="utf-8") as f:
            self.jugadores = json.load(f)

    @commands.command(name="empezar")
    async def empezar_impostor(self, ctx, juego: str):
        if juego != "impostor":
            return  # ignoramos si es para otro juego

        miembros = [m for m in ctx.guild.members if not m.bot]
        if len(miembros) < 3:
            await ctx.send("Se necesitan al menos 3 jugadores para jugar Impostor.")
            return

        jugador_real = random.choice(self.jugadores)
        impostor = random.choice(miembros)

        estado = {
            "jugador_real": jugador_real,
            "impostor_id": impostor.id,
            "jugadores": [m.id for m in miembros],
            "palabras": [],
            "votos": {},
            "fase": "palabras",  # otras: "votacion", "fin"
            "activos": [m.id for m in miembros]
        }

        self.partidas[ctx.guild.id] = estado

        for m in miembros:
            try:
                if m.id == impostor.id:
                    await m.send("🤫 Sos el **IMPOSTOR**. No sabés qué jugador le tocó a los demás. ¡Imitá y no te delates!")
                else:
                    await m.send(f"⚽ El jugador asignado es: **{jugador_real}**")
            except:
                await ctx.send(f"No pude enviar DM a {m.display_name}. Verificá tus permisos.")

        await ctx.send(
            f"🕵️‍♂️ Juego *Impostor* iniciado con {len(miembros)} jugadores.\n"
            f"Cada uno debe decir **una palabra** con `!palabra algo`.\n"
            f"Recordá: el impostor no sabe quién es el jugador."
        )

    @commands.command(name="palabra")
    async def decir_palabra(self, ctx, *, texto: str):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or partida["fase"] != "palabras":
            await ctx.send("No hay una partida activa o no estamos en la fase de palabras.")
            return

        jugador_id = ctx.author.id
        if jugador_id not in partida["activos"]:
            await ctx.send("No estás en la partida.")
            return

        if any(p["id"] == jugador_id for p in partida["palabras"]):
            await ctx.send("Ya dijiste tu palabra en esta ronda.")
            return

        partida["palabras"].append({
            "id": jugador_id,
            "nombre": ctx.author.display_name,
            "texto": texto
        })

        await ctx.send(f"✅ {ctx.author.display_name} ha dicho su palabra.")

        # Verificamos si ya hablaron todos
        if len(partida["palabras"]) == len(partida["activos"]):
            await ctx.send("🗳️ Todos dijeron su palabra. Fase de votación iniciada.")
            partida["fase"] = "votacion"
            partida["votos"] = {}

            resumen = "**🧠 Palabras de la ronda:**\n" + "\n".join(
                f"• {p['nombre']}: {p['texto']}" for p in partida["palabras"]
            )
            await ctx.send(resumen)
            await ctx.send("📣 Voten con `!voto @usuario` para intentar expulsar al impostor.")

    @commands.command(name="voto")
    async def votar(self, ctx, usuario: discord.Member):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or partida["fase"] != "votacion":
            await ctx.send("No estamos en fase de votación.")
            return

        jugador_id = ctx.author.id
        if jugador_id not in partida["activos"]:
            await ctx.send("No estás en esta partida.")
            return

        if jugador_id in partida["votos"]:
            await ctx.send("Ya votaste.")
            return

        votado_id = usuario.id
        if votado_id not in partida["activos"]:
            await ctx.send("Solo podés votar por jugadores activos.")
            return

        partida["votos"][jugador_id] = votado_id
        restantes = len(partida["activos"]) - len(partida["votos"])

        await ctx.send(f"🗳️ {ctx.author.display_name} ha votado. Faltan {restantes} voto(s).")

        # Si todos votaron
        if len(partida["votos"]) == len(partida["activos"]):
            conteo = {}
            for v in partida["votos"].values():
                conteo[v] = conteo.get(v, 0) + 1

            # Buscar máximos
            max_votos = max(conteo.values())
            candidatos = [uid for uid, count in conteo.items() if count == max_votos]

            if len(candidatos) > 1:
                await ctx.send("⚠️ Hay empate en la votación. Comienza otra ronda de palabras.")
                partida["fase"] = "palabras"
                partida["palabras"] = []
                partida["votos"] = {}
                return

            expulsado_id = candidatos[0]
            expulsado = ctx.guild.get_member(expulsado_id)
            partida["activos"].remove(expulsado_id)

            if expulsado_id == partida["impostor_id"]:
                await ctx.send(f"✅ Expulsaron a {expulsado.display_name}, que ERA el IMPOSTOR. ¡Ganaron los demás! 🎉")
                partida["fase"] = "fin"
            else:
                await ctx.send(f"❌ Expulsaron a {expulsado.display_name}, que NO era el impostor.")
                if len(partida["activos"]) == 2:
                    impostor = ctx.guild.get_member(partida["impostor_id"])
                    await ctx.send(f"👑 El impostor era {impostor.display_name}. ¡Ganó el IMPOSTOR!")
                    partida["fase"] = "fin"
                else:
                    await ctx.send("🔁 Comienza una nueva ronda. Decí una palabra con `!palabra algo`.")
                    partida["fase"] = "palabras"
                    partida["palabras"] = []
                    partida["votos"] = {}

    @commands.command(name="terminar")
    async def terminar_impostor(self, ctx):
        partida = self.partidas.get(ctx.guild.id)
        if not partida or partida["fase"] == "fin":
            await ctx.send("No hay un juego activo o ya terminó.")
            return

        self.partidas.pop(ctx.guild.id)
        await ctx.send("🛑 La partida de *Impostor* fue cancelada manualmente.")

async def setup(bot):
    await bot.add_cog(Impostor(bot))
