import discord
from discord.ext import commands

class StockPrediction(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def predict(self, ctx, *args):
        if args:
            await ctx.send(f"fetching data for stock {args[0]}")
        else:
            await ctx.send("no arguments provided! use !predict_help for help related to the predict command...")

    @commands.command()
    async def predict_help(self, ctx):
        await ctx.send("to use the prediction feature, simply type !predict followed by a stock ticker, i.e for stock information related to tesla, !predict tsla")

async def setup(client):
    await client.add_cog(StockPrediction(client=client))