import datetime

import pandas as pd
import requests
from loguru import logger
from pandas import DataFrame
import yfinance as yf
import threading
import time
import asyncio


# use asyncio and threading to implement a multi-threaded asyncronous data loader for price data from yahoo finance api


class PriceDataLoader():
    """
    Loader for OLHC
    """

    def __init__(self):
        self._data = None
        self._last_refresh_date = None
        self._data_map = {}

    def fetch_coin_price_data(self, symbol, start, end):
        logger.info(f"DataLoader: Fetching data for symbol {symbol}")
        df = yf.download(symbol, start, end)
        df = df.reset_index()
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df = df.set_index('Date')
        return df

    def get_now_date_str(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def load(self, symbol, start=None, end=None) -> DataFrame:
        logger.info(f"DataLoader: Starting data load at {self.get_now_date_str()} for symbol {symbol}")
        self._data = self.fetch_coin_price_data(symbol, start, end)
        self._last_refresh_date = self.get_now_date_str()
        return self._data

    #  Getters
    @property
    def data(self) -> DataFrame:
        return self._data

    @property
    def last_refresh_date(self) -> str:
        return self._last_refresh_date

    def last_price(self, symbol: str) -> float:
        if symbol in self._data_map:
            df = self._data_map[symbol]
            return df['Close'].iloc[-1]
        else:
            return 0
