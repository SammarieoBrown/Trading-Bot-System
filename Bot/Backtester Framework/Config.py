class Config():
    """
    Class for Bot configuration
    """

    def __init__(self, symbols, total_cash, cash_per_trade, data_fetch_interval):
        self._symbols = symbols
        self._cash_per_trade = cash_per_trade
        self._total_cash = total_cash
        self._data_fetch_interval = data_fetch_interval

    #  Getters
    @property
    def symbols(self) -> 'Tuple[str, ...]':
        return self._symbols

    @property
    def cash_per_trade(self) -> float:
        return self._cash_per_trade

    @property
    def total_cash(self) -> float:
        return self._total_cash

    @property
    def data_fetch_interval(self) -> int:
        return self._data_fetch_interval
