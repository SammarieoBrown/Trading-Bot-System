import datetime
import os
import sys
import time
from loguru import logger
from Broker import Broker
from PriceDataLoader import PriceDataLoader
from Strategy import Strategy


class Bot():
    """ Main Trading Bot class """

    def __init__(self, config: 'Config'):
        self._config = config
        self._price_loader = PriceDataLoader()
        self._broker = Broker(config.total_cash, self._price_loader)
        self._data: None
        self._is_running = False
        # Initial configurations
        self.setup_logging()

    def setup_logging(self):
        logger.remove()
        logger.add(sys.stdout, level="INFO")
        logger.add(f"logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log", rotation="1 day", level="DEBUG")

    def start(self):
        logger.info(f"Starting bot")
        self._is_running = True
        while self._is_running:
            #  For each symbol -> Get OHLC
            symbols = self._config.symbols
            for symbol in symbols:
                data_df = self._price_loader.load(symbol)
                strategy = Strategy(symbol, self._broker, self._config.cash_per_trade)
                strategy.execute(data_df)
            #  Check order status
            self._broker.check_order_status()
            #  Log some stats
            logger.info(self._broker.describe())
            time.sleep(self._config.data_fetch_interval)

    def stop(self):
        logger.info(f"Stopping bot")
        self._is_running = True
