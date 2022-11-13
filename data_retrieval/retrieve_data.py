import ccxt
import pandas as pd
import os
from datetime import datetime
import csv

def retrieve_data():
    """
    this function is used to retrieve data from FTX.
    """

    columns = ["time", "open", "high", "low", "close", "volume"]
    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    data_dir = os.path.abspath("..")+ "/raw_data/ticker_data/"
    exchange = ccxt.binance()
    start_ts = exchange.parse8601('2021-01-01 00:00:00')

    # Retrieve data from the exchange
    for ticker in ticker_list:
        check = ticker.replace("/", "_")
        file_path = os.path.isfile(data_dir+check+".csv")
        # Validate the data, return data & bool

        validate = validate_data(ticker, file_path, data_dir)

        # Data is valid, if CSV is exists and is not corrupted
        if validate == True:
            data = pd.read_csv(f"{data_dir}{check}.csv")
            update_data(data, ticker, exchange, columns)

        # Data is invalid, non-existent -> Write new data
        else:
            write_data(ticker, exchange, columns, data_dir, start_ts)
    #TODO: Return // dataframe with name of the ticker for further refernce

    return ticker_list, data
def validate_data(ticker, file_path,data_dir):
   validate = True
   ticker = ticker.replace("/", "_")

   if file_path == False:
       print(f"No CSV present for: {ticker}")
       validate = False


   # CSV empty or only headers present
   try:
        with open(f"{data_dir + ticker}.csv", 'r') as csvfile:
            csv_dict = [row for row in csv.DictReader(csvfile)]
            if len(csv_dict) == 0:
                print(f"The CSV is empty: {ticker}")
                validate = False
   except:
       print(f"Preparing new build for: {ticker}")
   # if os.path.getsize(data_dir) < 161:
   #      print(f'The CSV for {ticker} is empty')
   #      validate = False


   if validate is False and file_path == True:
        os.remove(f"{data_dir + ticker}.csv")

   return validate

def update_data(data, ticker, exchange, columns):
    data.drop(columns="Unnamed: 0", inplace=True)
    last_date = data["time"].iat[-1]
    data = data.iloc[:-1]
    ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=last_date, limit=1000)
    ohlcv_list = ohlcv.copy()

    while (len(ohlcv) == 1000):
        from_ts = ohlcv[-1][0]
        ohlcv.clear()
        ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
        ohlcv_list.extend(ohlcv)

    ohlcv_list = pd.DataFrame(ohlcv_list, columns=columns)
    data = pd.concat([data, ohlcv_list], ignore_index=True)

    last_date2 = datetime.fromtimestamp(last_date/ 1000).strftime('%Y-%m-%d %H:%M')
    print(f"Updated data for {ticker} per {last_date2}")
    return data

def write_data(ticker, exchange, columns, data_dir, start_ts):
    ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=start_ts, limit=1000)
    ohlcv_list = ohlcv.copy()

    while (len(ohlcv) == 1000):
        from_ts = ohlcv[-1][0]
        ohlcv.clear()
        ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
        ohlcv_list.extend(ohlcv)
        data = ohlcv_list

    ohlcv = pd.DataFrame(data, columns=columns)
    ticker = ticker.replace("/", "_")
    ohlcv.to_csv(f"{data_dir}{ticker}.csv", header=columns)

    print(f"Building new CSV for: {ticker}")


if __name__ == "__main__":
    retrieve_data()