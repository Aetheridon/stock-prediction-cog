from datetime import date
from io import BytesIO

import discord
from discord.ext import commands

import yfinance as yf

from prophet import Prophet
from prophet.plot import plot_plotly

import matplotlib.pyplot as plt

class StockPrediction(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.TODAY = date.today().strftime("%Y-%m-%d")

    def plot_data(self, data, ticker, period, company_name):
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

        plt.title(company_name)

        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()

        buffer.seek(0)
        return buffer

    def get_data(self, ticker, start):
        data = yf.download(ticker, start, self.TODAY)
        data.reset_index(inplace=True)
        return data

    @commands.command()
    async def predict(self, ctx, *args):
        if args:

            ticker = args[0]

            if len(args) > 1:
                user_period = int(args[1])
            
            else:
                user_period = 365
            
            if len(args) > 2:
                start = args[2]
            
            else:
                start = "2015-1-1"

            try:
                company_name = yf.Ticker(ticker)
                company_name = company_name.info["longName"]

                await ctx.send(f"Fetching data for company: `{company_name}`")
                
                data = self.get_data(ticker=ticker, start=start)
                buffer = self.plot_data(data=data, ticker=ticker, period=user_period, company_name=company_name)
                await ctx.send(file=discord.File(buffer, filename="plot.png"))

            except KeyError:
                await ctx.send(f"Invalid tick: {ticker}")

        else:
            await ctx.send("No arguments supplied! check the usage of the bot with `!predict_help`")

    @commands.command()
    async def predict_help(self, ctx):
        await ctx.send(f"""```
{'='*5} Supported items to predict: {'='*5}
    Stocks, Crypto, Commodities\n 
{'='*5} Usage: {'='*5}
    !predict [tick] [period of prediction, default: 365] [start date, default: 2015-1-1]```
        """)

async def setup(client):
    await client.add_cog(StockPrediction(client=client))