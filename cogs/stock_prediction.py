import discord
from discord.ext import commands

class StockPrediction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def predict(self, ctx):
        await ctx.send("predicting")

async def setup(client):
    await client.add_cog(StockPrediction(client=client))