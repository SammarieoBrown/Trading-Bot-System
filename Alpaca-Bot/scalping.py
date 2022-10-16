import pandas as pd
import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.requests import GetOrdersRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.trend import VortexIndicator
from ta.volatility import BollingerBands
import time
import datetime as dt
import matplotlib.pyplot as plt


# create a bot that will buy crypto when the price crosses above the moving average and close that position when the
# price is above the upper bollinger band


# the market data class will be used to get the historical data for the crypto asset using alpaca and calculate the
# moving average and bollinger bands for the asset
# pass in the user authentication details
class MarketData:
    def __init__(self, api_key, secret_key):
        self.client = TradingClient(api_key=api_key, secret_key=secret_key)
        self.crypto = CryptoHistoricalDataClient()

    # get the historical data for the crypto asset
    def get_historical_data(self, symbol, lookback):
        start_date = dt.date.today() - dt.timedelta(lookback)
        end_date = dt.date.today()
        start_date = dt.datetime.combine(start_date, dt.datetime.min.time())

        request_params = CryptoBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute,
            # start=start_date
        )

        bars = self.crypto.get_crypto_bars(request_params)

        # create new columns for the moving average and bollinger bands and populate them with the values
        # calculated from the historical data

        bars = bars.df
        # drop index column
        bars = bars.drop(columns=['index'])

        bars['ema'] = EMAIndicator(bars.close, 20).ema_indicator()
        bars['rsi'] = RSIIndicator(bars.close, 14).rsi()
        bb = BollingerBands(bars.close, 20, 2)
        bars['bb_upper'] = bb.bollinger_hband()
        bars['bb_lower'] = bb.bollinger_lband()
        bars['bb_middle'] = bb.bollinger_mavg()

        # replace the NaN values with 0 and return the dataframe
        bars.fillna(0, inplace=True)

        # iterate through each symbol and if the yesterday's close is lower than today's price and the price is above
        # the moving average then buy
        bars['buy'] = np.where((bars['close'] > bars['ema']) & (bars['close'].shift(1) < bars['close']), 1, 0)

        # plot the buy signal on the chart to see if it is working correctly
        plt.plot(bars['close'])
        plt.plot(bars['ema'])
        plt.plot(bars['bb_upper'])
        plt.plot(bars['bb_lower'])
        plt.plot(bars['bb_middle'])
        plt.scatter(bars.index, bars['close'], c=bars['buy'], cmap='RdYlGn', marker='^', s=100)
        plt.show()


        # convert to dataframe
        return bars


# strategy class will be used to determine when to buy and sell the crypto asset based on the moving average and
# bollinger bands
class Strategy:
    def __init__(self, market_data):
        self.market_data = market_data

    # determine when to buy the crypto asset
    def buy_signal(self, symbol, lookback):
        # get the historical data
        df = self.market_data.get_historical_data(symbol, lookback)

        # if the current price is above the moving average and the current price is above the upper bollinger band
        # then return true
        if df.close[-1] > df.ema[-1] and df.close[-1] > df.bb_upper[-1]:
            return True
        else:
            return False

    # determine when to sell the crypto asset
    def sell_signal(self, symbol, lookback):
        # get the historical data
        df = self.market_data.get_historical_data(symbol, lookback)

        # if the current price is above the upper bollinger band then return true
        if df.close[-1] > df.bb_upper[-1]:
            return True
        else:
            return False


# the trading class will be used to place the buy and sell orders for the crypto asset
# checks the account balance to ensure there is enough cash to place the order and then places the order
# checks if the position is already in the market and if it is then it will not place another order
class Trading:
    def __init__(self, api_key, secret_key):
        self.client = TradingClient(api_key=api_key, secret_key=secret_key)

        # a function that checks if the position is already in the market
        # Check Whether Account Currently Holds Symbol
        def check_positions(symbol):
            positions = self.client.get_all_positions()
            for p in positions:
                if p.symbol == symbol:
                    return float(p.qty)
            return 0

        # a function that checks the account balance to ensure there is enough cash to place the order
        # Check Account Balance
        def check_balance():
            account = self.client.get_account()
            return float(account.cash)

        # a function that places the buy order
        # Place Buy Order
        def buy_order(symbol, qty):
            order = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            self.client.submit_order(order)

        # a function that close the position
        # Close Position
        def close_position(symbol):
            self.client.close_position(symbol)

        # no sell order, buy order only


# test the market data class

def main():
    api_key = 'PKFZSPYZXB1ZDPPZ1UZU'
    secret_key = '7KFPD5JYczbvPstNCtbF4GzVrblxBZc00q06LVPx'
    market_data = MarketData(api_key, secret_key)
    market_data.get_historical_data('BTC/USD', 1)
    print(len(market_data.get_historical_data('BTC/USD', 1)))


if __name__ == '__main__':
    main()

"""
# buy signal
        if (data['rsi'].iloc[-1] < 30) and (data['close'].iloc[-1] < data['ema'].iloc[-1]) and (
                data['close'].iloc[-1] < data['close'].iloc[-2]):
            return 'buy'
        # sell signal
        elif (data['rsi'].iloc[-1] > 70) and (data['close'].iloc[-1] > data['ema'].iloc[-1]) and (
                data['close'].iloc[-1] > data['close'].iloc[-2]):
            return 'sell'

"""

string = 'BTC/USD'
# remove the / from the string
string = string.replace('/', '')