import uuid

from Utils import *


class Order:
    """ Class for managing orders """

    def __init__(self, symbol: str,
                 position: Positions,
                 side: Side,
                 size: float,
                 limit_price: float = None,
                 stop_price: float = None):
        self._id = str(uuid.uuid4())
        self._symbol = symbol
        self._position = position
        self._side = side
        self._size = size
        self._price = 0
        self._limit_price = limit_price
        self._stop_price = stop_price
        self._status = OrderStatus.PENDING

    def describe(self):
        return f"<Order id: {self._id} symbol: {self._symbol} position: {self._position} limit: {self._limit_price} stop: {self._stop_price}>"

    # Getters
    @property
    def id(self) -> str:
        return self._id

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def position(self) -> Positions:
        return self._position

    @property
    def side(self) -> Side:
        return self._side

    @property
    def size(self) -> float:
        return self._size

    @property
    def price(self) -> float:
        return self._price

    @property
    def limit_price(self) -> float:
        return self._limit_price

    @property
    def stop_price(self) -> float:
        return self._stop_price

    @property
    def status(self) -> OrderStatus:
        return self._status

    #  Setters
    def set_status(self, status):
        self._status = status

    def set_price(self, price):
        self._price = price
