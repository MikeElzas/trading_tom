
from datetime import datetime, timedelta
import pandas as pd



def retrieve_data(days, ticker, timeframe):
    """
    this function is used to retrieve data from FTX.
    days = the amount of days the user would like to look back.
    ticker = the ticker the user wants to retrieve data on e.g. BTC/USD.
    timeframe = how often the data should get retrieved e.g. 1m, 1h.
    """
    import ccxt

    #here the timedelta is calculated based on the number of days
    since = datetime.utcnow() - timedelta(days=days)
    since_ms = int(since.timestamp()) * 1000

    #retrieve data from the exchange
    ftx = ccxt.ftx()
    data = ftx.fetch_ohlcv(symbol = ticker,timeframe = timeframe, since = since_ms )

    #convert the data to a DataFrame
    ohlcv = pd.DataFrame(data, columns = ["time", "open", "high", "low", "close", "volume"])

    #converting the time column to a proper date format
    ohlcv['time'] = ohlcv['time'].apply(lambda x : datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M'))


    #eventually we use this function so the user can fill in a date format and it gets converted
    #import time, datetime
    #print(time.mktime(datetime.datetime.strptime(string,"%d/%m/%Y").timetuple()))


    return ohlcv
