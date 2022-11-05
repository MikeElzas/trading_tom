import ccxt
import pandas as pd
import os

def retrieve_data():
    """
    this function is used to retrieve data from FTX.
    days = the amount of days the user would like to look back.
    ticker = the ticker the user wants to retrieve data on e.g. BTC/USD.
    timeframe = how often the data should get retrieved e.g. 1m, 1h.
    """

    columns = ["time", "open", "high", "low", "close", "volume"]
    ticker_list = ["BTC/USDT", "ETH/USDT"]
    data_dir = os.path.abspath("..")+ "/data/ticker_data/"


    #retrieve data from the exchange
    for ticker in ticker_list:
        ftx = ccxt.ftx()
        from_ts = ftx.parse8601('2021-01-01 00:00:00')
        ohlcv = ftx.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
        ohlcv_list = ohlcv.copy()
        #if the len of OHLCV is 1000 it indicates that there is still more data left, if it is less then we know we are at the end
        while(len(ohlcv)==1000):
            from_ts = ohlcv[-1][0]
            ohlcv.clear()
            ohlcv = ftx.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
            ohlcv_list.extend(ohlcv)

    #convert the data to a DataFrame and write it to a local csv file in the ticker_data folder
        ohlcv = pd.DataFrame(ohlcv_list, columns=columns)
        ticker = ticker.replace("/", "_")
        ohlcv.to_csv(f"{data_dir}{ticker}.csv", header=columns)
