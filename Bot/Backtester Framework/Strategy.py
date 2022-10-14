from Utils import *
from Config import Config
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator


class Strategy:
    def __init__(self, broker, price_loader, config):
        self._broker = broker
        self._price_loader = price_loader
        self._config = config

    def execute(self, data_df):
        """
        Execute the strategy
         # Loop through the data and if rsi is below 30, buy and if rsi is above 70, sell (short)
        # Config accepts the symbol and the cash per trade
        :param data_df: Dataframe with price data
        """
        #  Get RSI
        data_df['rsi'] = RSIIndicator(close=data_df['Close'], window=14).rsi()
        #  Loop through the data and if rsi is below 30, buy and if rsi is above 70, sell (short)
        # check if the last rsi value is below 30 and if the last rsi value is above 70
        last_rsi = data_df['rsi'].iloc[-1]
        if last_rsi < 30:
            #self._broker.buy(data_df)
            print('buy')
        elif last_rsi > 70:
            #self._broker.sell(data_df)
            print('sell')

