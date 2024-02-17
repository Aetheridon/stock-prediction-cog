'''This is a simple bot to test the functionality of the cog!'''

import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()

token = input("Enter your token\n> ")
client = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    await client.load_extension("cogs.stock_prediction")

asyncio.run(load_extensions())
client.run(token)
