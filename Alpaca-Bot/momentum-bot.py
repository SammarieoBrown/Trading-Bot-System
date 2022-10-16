# Import Dependencies
import numpy as np
import pandas as pd
import alpaca_trade_api as tradeapi
import datetime as dt
import asyncio
from alpaca_trade_api.stream import Stream

# API Credentials
# API Credentials
ALPACA_API_KEY = 'PKFZSPYZXB1ZDPPZ1UZU'
ALPACA_SECRET_KEY = '7KFPD5JYczbvPstNCtbF4GzVrblxBZc00q06LVPx'
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, 'https://paper-api.alpaca.markets')
api.close_all_positions()

# Date Variables
start_date = dt.date.today() - dt.timedelta(days=60)
end_date = dt.date.today()


# Check Whether Account Currently Holds Symbol
def check_positions(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            return float(p.qty)
    return 0


# Cross Sectional Momentum Bot Function
def cross_sectional_momentum(bar):
    try:
        # Get the Latest Data
        dataframe = pd.DataFrame()
        symbols = ['BTCUSD', 'ETHUSD', 'DOGEUSD', 'SHIBUSD', 'MATICUSD', 'ALGOUSD', 'AVAXUSD', 'LINKUSD', 'SOLUSD']
        for symbol in symbols:
            data = api.get_crypto_bars(symbol, tradeapi.TimeFrame(1, tradeapi.TimeFrameUnit.Day), start=start_date,
                                       end=end_date, exchanges=['FTXU']).df['close']
            data = pd.DataFrame(data).rename(columns={"close": str(symbol)})
            dataframe = pd.concat([dataframe, data], axis=1, sort=False)

        returns_data = dataframe.apply(func=lambda x: x.shift(-1) / x - 1, axis=0)

        # Calculate Momentum Dataframe
        momentum_df = returns_data.apply(func=lambda x: x.shift(1) / x.shift(7) - 1, axis=0)
        momentum_df = momentum_df.rank(axis=1)
        for col in momentum_df.columns:
            momentum_df[col] = np.where(momentum_df[col] > 8, 1, 0)

        # Get Symbol with Highest Momentum
        momentum_df['Buy'] = momentum_df.astype(bool).dot(momentum_df.columns)
        buy_symbol = momentum_df['Buy'].iloc[-1]
        old_symbol = momentum_df['Buy'].iloc[-2]

        # Account Details
        current_position = check_positions(symbol=buy_symbol)
        old_position = check_positions(symbol=old_symbol)

        # No Current Positions
        if current_position == 0 and old_position == 0:
            cash_balance = api.get_account().non_marginable_buying_power
            api.submit_order(buy_symbol, notional=cash_balance, side='buy')
            message = f'Symbol: {buy_symbol} | Side: Buy | Notional: {cash_balance}'
            print(message)

        # No Current Position and Yes Old Position
        if current_position == 0 and old_position == 1:
            api.close_position(old_position)
            message = f'Symbol: {old_symbol} | Side: Sell'
            print(message)

            cash_balance = api.get_account().non_marginable_buying_power
            api.submit_order(buy_symbol, notional=cash_balance, side='buy')
            message = f'Symbol: {buy_symbol} | Side: Buy | Notional: {cash_balance}'
            print(message)

        print("-" * 20)

    except Exception as e:
        print(e)


# Create instance of Alpaca data streaming API
alpaca_stream = tradeapi.Stream(ALPACA_API_KEY, ALPACA_SECRET_KEY, raw_data=True, )


# crypto_exchanges=['FTXU'])

# Create handler for receiving live bar data
async def on_crypto_bar(bar):
    print(bar)
    cross_sectional_momentum(bar)


# Subscribe to data and assign handler
alpaca_stream.subscribe_updated_bars(on_crypto_bar, 'BTCUSD', 'ETHUSD', 'DOGEUSD', 'SHIBUSD', 'MATICUSD', 'ALGOUSD',
                                     'AVAXUSD', 'LINKUSD', 'SOLUSD')

# Start streaming of data
alpaca_stream.run()
