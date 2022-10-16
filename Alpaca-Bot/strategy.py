#!/usr/bin/python3

import datetime as dt
import time

import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest, ReplaceOrderRequest, TrailingStopOrderRequest
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands


class TradingBot:
    def __init__(self, symbol, lookback, risk):
        self.symbol = symbol
        self.lookback = lookback
        self.risk = risk



    def stream_data(self, symbol, lookback):
        # date formatting
        start_date = dt.date.today() - dt.timedelta(days=lookback)
        start_date = dt.datetime.combine(start_date, dt.datetime.min.time())
        end_date = dt.date.today()
        end_date = dt.datetime.combine(end_date, dt.datetime.min.time())

        request_params = CryptoBarsRequest(
            symbol_or_symbols=symbol,  # Can be a list of symbols or a single symbol ['BTC/USD', 'ETH/USD'] or 'BTC/USD'
            timeframe=TimeFrame.Minute,
            start=start_date,
        )
        cryptoClient = CryptoHistoricalDataClient()
        data = cryptoClient.get_crypto_bars(request_params)
        data = data.df
        data = data.reset_index(pd.Index(['symbol']))

        # calculate indicators
        data['ema'] = EMAIndicator(data.close, 20).ema_indicator()
        data['rsi'] = RSIIndicator(data.close, 14).rsi()
        bb = BollingerBands(data.close, 20, 2)
        data['bb_upper'] = bb.bollinger_hband()
        data['bb_lower'] = bb.bollinger_lband()
        data['bb_middle'] = bb.bollinger_mavg()

        # replace the NaN values with 0 and return the dataframe
        data.fillna(0, inplace=True)
        return data

    def check_positions(self, symbol):
        trading_client = TradingClient('PKFZSPYZXB1ZDPPZ1UZU', '7KFPD5JYczbvPstNCtbF4GzVrblxBZc00q06LVPx')

        positions = trading_client.get_all_positions()
        # print(positions)
        for symbols in symbol:
            symbol = symbols.replace('/', '')
        # count the number of positions  with the symbol we are looking for and return the number of positions we
        # have open for that symbol
        return len([position for position in positions if position.symbol == symbol])

    def strategy(self, data, symbol, risk):
        """
        If the RSI is below 30 and the price is below the EMA and the price is below the previous price, buy the asset. If the
        RSI is above 70 and the price is above the EMA and the price is above the previous price, sell the asset

        :param data: the dataframe that contains the data for the symbol in question
        :param symbol: the symbol of the asset we want to trade
        :return: The order that was placed.
        """
        trading_client = TradingClient('PKFZSPYZXB1ZDPPZ1UZU', '7KFPD5JYczbvPstNCtbF4GzVrblxBZc00q06LVPx')
        account = trading_client.get_account()
        cash = float(account.non_marginable_buying_power)
        positions = self.check_positions(symbol)

        # use 5% of the cash to buy the asset
        cash_to_use = cash * risk
        # calculate the number of assets to buy
        qty = cash_to_use / data.close.iloc[-1]
        qty = round(qty, 3)
        print("bot running at: ", dt.datetime.now())

        # if we have no positions for the symbol in question, and we have enough cash to buy the asset This is the
        # buy condition. If we have no positions for the symbol in question, and we have enough cash to buy the
        # asset, we will buy the asset.
        if positions == 0 and cash_to_use > 0:

            # buy the asset
            if data['close'].iloc[-2] < data['close'].iloc[-1]:
                # place the order
                order = trading_client.submit_order(
                    MarketOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.GTC,
                    )
                )
                print('Buy order placed for ' + symbol + ' at ' + str(data.close.iloc[-1]))
                return order
            # check if we have a position for the symbol in question and if we do close it
        elif positions > 0:

            # sell the asset
            if data['close'].iloc[-2] > data['close'].iloc[-1]:
                # place the order
                symbol = symbol.replace('/', '')
                order = trading_client.close_position(
                    symbol_or_asset_id=symbol
                )
                print('Sell order placed for ' + symbol + ' at ' + str(data.close.iloc[-1]))
                return order
        else:
            return None

    def run(self):
        while True:
            data = self.stream_data(self.symbol, self.lookback)
            self.strategy(data, self.symbol, self.risk)
            time.sleep(1)


if __name__ == '__main__':
    BTC = ['BTC/USD']
    ETH = ['ETH/USD']
    lookback = 1
    risk = 0.3
    BTC_bot = TradingBot(BTC, lookback, risk)
    ETH_bot = TradingBot(ETH, lookback, risk)
    ETH_bot.run()
    BTC_bot.run()

