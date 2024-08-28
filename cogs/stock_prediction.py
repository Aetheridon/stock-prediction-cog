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
        self.TODAY = date.today().strftime("%Y-%m-%d")

    def plot_data(self, data, ticker, period, company_name):

        highest_price = data['High'].max()

        highest_price_data = data[data['High'] == highest_price]

        date_of_highest_price = highest_price_data['Date'].iloc[0]

        current_price = data['Close'].iloc[-1]

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

        #TODO: cleanup annotations in upcoming code overhaul

        plt.annotate(
            f'Highest Price: ${highest_price:,.2f}',
            xy=(0.95, 0.99),
            xycoords='figure fraction',
            textcoords='figure fraction',
            ha='right',
            va='top', 
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")
        )

        plt.annotate(
            f'Date of Highest Price: {date_of_highest_price}',
            xy=(0.95, 0.95),
            xycoords='figure fraction',
            textcoords='figure fraction',
            ha='right',
            va='top',
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")
        )

        plt.annotate(
            f'Current Price: ${current_price:,.2f}',
            xy=(0.95, 0.91),
            xycoords='figure fraction',
            textcoords='figure fraction',
            ha='right',
            va='top',
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")
        )

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
    async def help_me(self, ctx, *args):

        if len(args) > 0:
            
            match args[0]:
                case "bot":
                    await ctx.send("to use the bot, simply use `!predict <ticker> <period of prediction: defaults to 365> <start date of the data: defaults to 2015-1-1>`")
                case "ticker":
                    await ctx.send("a stock ticker is a shorthand symbol used to identify a specific publicy traded company's stock")
                case "crypto":
                    await ctx.send("this cog supports prediction of crypto, however, you must use the same ticker as shown on yahoo finance's website, i.e Bitcoin is `BTC-USD`")
                case "commodities":
                    await ctx.send("this cog supports prediction of commodities, you must use the ticker as shown on yahoo finance, i.e Gold is GC=F (as of 05/06/2024 this seems to be bugged and the bot can no longer predict commodities, an issue on the github has been submitted and this is being investigated)")
                case _:
                    await ctx.send(f"no such help for category: {args[0]}")

        else:
            await ctx.send("""               
            Heres a list of things to get help with! (use !help <option>)               
            - bot: general bot usage
            - ticker: tells you what a ticker is, a fundamental part of the market and using this bot
            - crypto: how the bot supports prediction of cryptocurrencies
            - commodities: how the bot supports prediction of commodities
             """)

async def setup(client):
    await client.add_cog(StockPrediction(client=client))