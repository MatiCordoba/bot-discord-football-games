import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # importante para leer mensajes

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

async def main():
    # Cargamos las extensiones correctamente con await
    await bot.load_extension("cogs.adivina_jugador")
    await bot.load_extension("cogs.impostor")
    await bot.load_extension("cogs.general")
    await bot.start(os.getenv("DISCORD_TOKEN"))

# Ejecutar el bot correctamente
import asyncio
asyncio.run(main())