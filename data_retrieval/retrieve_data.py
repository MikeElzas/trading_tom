import ccxt
import pandas as pd
import os
from datetime import datetime
import csv
from big_query import cloud_get_data, cloud_save_data, cloud_validate_data, cloud_append_data
from local_disk import local_get_data, local_save_data, local_validate_data, local_append_data

def retrieve_data():
    """
    this function is used to retrieve data from FTX.
    """

    columns = ["time", "open", "high", "low", "close", "volume"]
    ticker_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    exchange = ccxt.binance()
    start_ts = exchange.parse8601('2021-01-01 00:00:00')

    # Retrieve data from the exchange
    for ticker in ticker_list:
        check = ticker.replace("/", "_")

        # Validate the data, return data & bool
        if os.environ.get('DATA_SOURCE') == 'local':
            validate = local_validate_data(ticker)
            if validate == True:
                data = local_get_data(ticker)
                data = update_data(data,ticker,exchange,columns)
                local_append_data(data,ticker,columns)
            else: write_data(ticker, exchange, columns, start_ts)

        elif os.environ.get('DATA_SOURCE') == 'cloud':
            validate = cloud_validate_data(ticker)
            if validate == True:
                data = cloud_get_data(ticker)
                data = update_data(data,ticker,exchange,columns)
                cloud_append_data(data,ticker)
            else: write_data(ticker, exchange, columns, start_ts)

        else:
            raise ValueError(f"Value in .env{os.environ.get('DATA_SOURCE')} is unknown")



    #TODO: Return // dataframe with name of the ticker for further refernce

    return ticker_list, data



def update_data(data, ticker, exchange, columns):
    #data.drop(columns="Unnamed: 0", inplace=True)
    #last_date = data["time"].iat[-1]
    last_date = data["time"].max()
    data = data[data['time']!=last_date]


    print(last_date)
    print(data)

    ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=last_date, limit=1000)
    ohlcv_list = ohlcv.copy()

    while (len(ohlcv) == 1000):
        from_ts = ohlcv[-1][0]
        ohlcv.clear()
        ohlcv = exchange.fetch_ohlcv(ticker, '1h', since=from_ts, limit=1000)
        ohlcv_list.extend(ohlcv)

    ohlcv_list = pd.DataFrame(ohlcv_list, columns=columns)
    #data = pd.concat([data, ohlcv_list], ignore_index=True)
    #ohlcv_list.to_csv('log.csv', mode='a', index=False, header=False)

    last_date2 = datetime.fromtimestamp(last_date/ 1000).strftime('%Y-%m-%d %H:%M')
    print(ohlcv_list)
    print(f"Updated data for {ticker} per {last_date2}")
    return ohlcv_list

def write_data(ticker, exchange, columns, start_ts):
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
    #ohlcv.to_csv(f"{data_dir}{ticker}.csv", header=columns)

    #save data based on data_source type
    if os.environ.get('DATA_SOURCE') == 'local':
        local_save_data(ohlcv,ticker,columns)

    elif os.environ.get('DATA_SOURCE') == 'cloud':
        cloud_save_data(ohlcv,ticker)

    else:
        raise ValueError(f"Value in .env{os.environ.get('DATA_SOURCE')} is unknown")

    print(f"Building new CSV for: {ticker}")


if __name__ == "__main__":
    retrieve_data()
