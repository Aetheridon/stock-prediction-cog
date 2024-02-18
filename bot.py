'''This is a simple bot to test the functionality of the cog!'''

import sys

import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()

token = sys.argv[1]
client = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    await client.load_extension("cogs.stock_prediction")

asyncio.run(load_extensions())
client.run(token)
