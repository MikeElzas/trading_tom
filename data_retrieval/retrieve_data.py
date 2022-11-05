import ccxt
import pandas as pd
import os

def retrieve_data():
    """
    this function is used to retrieve data from FTX.
    """

    columns = ["time", "open", "high", "low", "close", "volume"]
    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    data_dir = os.path.abspath("..")+ "/trading_tom/raw_data/ticker_data/"
    ftx = ccxt.ftx()

    #retrieve data from the exchange
    for ticker in ticker_list:
        check = ticker.replace("/", "_")
        file_path =os.path.isfile(data_dir+check+".csv")

        #first check whether the .csv file already exists
        if file_path == True :
            data = pd.read_csv(f"{data_dir}{check}.csv")
            data.drop(columns = "Unnamed: 0", inplace=True)
            last_date = data["time"].iat[-1]
            data = data.iloc[:-1]
            ohlcv = ftx.fetch_ohlcv(ticker, '1h', since=last_date, limit=1000)

            ohlcv_list = ohlcv.copy()

            while(len(ohlcv)==1000):
                from_ts = ohlcv[-1][0]
                ohlcv.clear()
                ohlcv = ftx.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
                ohlcv_list.extend(ohlcv)


            ohlcv_list = pd.DataFrame(ohlcv_list, columns = columns)
            data = pd.concat([data,ohlcv_list], ignore_index=True)
        #if the file does not already exist, we make a new file
        else:
            from_ts = ftx.parse8601('2021-01-01 00:00:00')
            ohlcv = ftx.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
            ohlcv_list = ohlcv.copy()
            #if the len of OHLCV is 1000 it indicates that there is still more data left, if it is less then we know we are at the end
            while(len(ohlcv)==1000):
                from_ts = ohlcv[-1][0]
                ohlcv.clear()
                ohlcv = ftx.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
                ohlcv_list.extend(ohlcv)
                data = ohlcv_list

    #convert the data to a DataFrame and write it to a local csv file in the ticker_data folder
        ohlcv = pd.DataFrame(data, columns=columns)
        ticker = ticker.replace("/", "_")
        ohlcv.to_csv(f"{data_dir}{ticker}.csv", header=columns)

    return ticker_list
