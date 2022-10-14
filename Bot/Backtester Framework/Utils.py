from enum import Enum


class Positions(Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'


class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class OrderStatus(Enum):
    PENDING = 'PENDING'
    CANCELED = 'CANCELED'
    FILLED = 'FILLED'
