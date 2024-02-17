from datetime import date
from io import BytesIO

import discord
from discord.ext import commands

import yfinance as yf

from prophet import Prophet
from prophet.plot import plot_plotly

import matplotlib.pyplot as plt

import pandas as pd

class StockPrediction(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.START = "2015-01-01"
        self.TODAY = date.today().strftime("%Y-%m-%d")

    def plot_data(self, data, ticker, period):
        df_train = data.reset_index()[["Date", "Close"]]
        df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

        m = Prophet()
        m.fit(df_train)
        
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)
        
        plt.figure(figsize=(10,  6))
        plt.plot(df_train["ds"], df_train["y"], label="Actual", color="blue")
        plt.plot(forecast["ds"], forecast["yhat"], label="Predicted", color="red")
        plt.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], color="pink", alpha=0.5)
        plt.title(f"{ticker} Stock Price Prediction")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()

        buffer.seek(0)
        return buffer

    def get_data(self, ticker):
        data = yf.download(ticker, self.START, self.TODAY)
        data.reset_index(inplace=True)
        return data

    @commands.command()
    async def predict(self, ctx, *args):
        try:
            if args:
                ticker = args[0]
                user_period = int(args[1])
                await ctx.send(f"fetching data for stock {ticker} and plotting...")
                data = self.get_data(ticker=ticker)
                buffer = self.plot_data(data=data, ticker=ticker, period=user_period)
                await ctx.send(file=discord.File(buffer, filename="plot.png"))

            else:
                await ctx.send("no arguments provided! use !predict_help for help related to the predict command...")
                
        except IndexError:
            await ctx.send("please supply a period for prediction!")

    @commands.command()
    async def predict_help(self, ctx):
        await ctx.send("to use the prediction feature, simply type !predict followed by a stock ticker, i.e for stock information related to tesla, !predict tsla, the second argument will be periods of prediction.")

async def setup(client):
    await client.add_cog(StockPrediction(client=client))