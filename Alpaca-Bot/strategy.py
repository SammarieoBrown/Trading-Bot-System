#!/usr/bin/python3

import datetime as dt
import time

import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest, ReplaceOrderRequest, TrailingStopOrderRequest
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
from loguru import logger


class TradingBot():
    def __init__(self, symbol, lookback, risk):
        super().__init__()
        self.symbol = symbol
        self.lookback = lookback
        self.risk = risk
        self.trading_client = TradingClient('PK8AWLHHM9R99WPKQ73I', 'ACdKis9STB3paVP7H3NoBdMSxmMofUKQQXAE2aNa')

    def stream_crypto_data(self, symbol, lookback):
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
        data['fast_ema'] = EMAIndicator(data.close, 20).ema_indicator()
        data['slow_ema'] = EMAIndicator(data.close, 50).ema_indicator()
        data['rsi'] = RSIIndicator(data.close, 14).rsi()
        bb = BollingerBands(data.close, 20, 2)
        data['bb_upper'] = bb.bollinger_hband()
        data['bb_lower'] = bb.bollinger_lband()
        data['bb_middle'] = bb.bollinger_mavg()

        # replace the NaN values with 0 and return the dataframe
        data.fillna(0, inplace=True)

        # log the data

        return data

    def check_positions(self, symbol):

        positions = self.trading_client.get_all_positions()
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
        account = self.trading_client.get_account()

        # log cash available

        cash = float(account.non_marginable_buying_power)
        logger.info(f'Cash available: {cash}')
        positions = self.check_positions([symbol])
        logger.info(f'Number of positions: {positions}')

        # use 5% of the cash to buy the asset
        cash_to_use = cash * risk
        # calculate the number of assets to buy
        qty = cash_to_use / data.close.iloc[-1]
        qty = round(qty, 3)
        # log  the running of the bad

        # print("bot running at: ", dt.datetime.now())
        logger.info(f"bot running at: {dt.datetime.now()}")

        # if we have no positions for the symbol in question, and we have enough cash to buy the asset This is the
        # buy condition. If we have no positions for the symbol in question, and we have enough cash to buy the
        # asset, we will buy the asset.
        if positions == 0 and cash_to_use > 0:

            # crossover function The `source1`-series is defined as having crossed over `source2`-series if,
            # on the current bar, the value of `source1` is greater than the value of `source2`, and on the previous
            # bar, the value of `source1` was less than or equal to the value of `source2`. ta.crossover(source1,
            # source2) → series bool RETURNS true if `source1` crossed over `source2` otherwise false. ARGUMENTS
            # source1 (series int/float) First data series. source2 (series int/float) Second data series. crossover
            # = -> bool true if `source1` crossed over `source2` otherwise false.
            crossover = data.close.iloc[-1] > data.fast_ema.iloc[-1]\
                        and data.close.iloc[-2] < data.fast_ema.iloc[-2]

            # buy the asset if fast EMA is crossover the slow EMA
            if crossover and (data.close.iloc[-1] < data.bb_upper.iloc[-1]):
                # place the order
                order = self.trading_client.submit_order(
                    MarketOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.GTC,

                    )
                )
                signal = f"BUY {qty} {symbol}"
                logger.info(signal)
                # convert the order to a dataframe and log the order
                order = order.__dict__
                # log the order that was placed
                logger.info(f"Order placed: {order}")
                logger.info(f'Buy order placed for {qty} shares of {symbol} at {data.close.iloc[-1]}')
                return order
            # check if we have a position for the symbol in question and if we do close it
        elif positions > 0:

            # sell the asset close is over the upper bollinger band
            if data['close'].iloc[-1] > data['bb_upper'].iloc[-1]:
                # place the order
                symbol = symbol.replace('/', '')
                order = self.trading_client.close_position(
                    symbol_or_asset_id=symbol
                )
                # convert the order to a dictionary
                order = order.__dict__
                # log the order that was placed
                logger.info(f"Order placed: {order}")
                logger.info(f'Sell order placed for {qty} shares of {symbol} at {data.close.iloc[-1]}')
                return order
        else:
            return None

    # a function that checks if the connection to the Alpaca API is working and if it is not, it will try to
    # reconnect to the API every 5 seconds until it is able to connect to the API again
    def check_connection(self):
        # create a connection to the Alpaca API
        # check if the connection to the Alpaca API is working
        try:
            self.trading_client.get_account()
            return True
        except:
            # if the connection to the Alpaca API is not working, try to reconnect to the API every 5 seconds until
            # it is able to connect to the API again
            while True:
                try:
                    self.trading_client.get_account()
                    return True
                except:
                    time.sleep(5)

    def run(self):
        # check if the connection to the Alpaca API is working
        if self.check_connection():
            while True:
                data = self.stream_crypto_data(self.symbol, self.lookback)
                self.strategy(data, self.symbol, self.risk)
                time.sleep(1)


def main():
    symbol = ['BTC/USD', 'ETH/USD']
    for symbols in symbol:
        bot = TradingBot(symbols, 1, 0.01)
        bot.run()


if __name__ == '__main__':
    main()
